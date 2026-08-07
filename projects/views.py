from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from notifications.utils import send_workspace_notification
from workspaces.models import Membership, Workspace

from .models import Board, Project, ProjectMember, Task
from .permissions import (
    IsProjectAdmin,
    IsProjectMember,
    IsProjectOwnerOrAdmin,
    IsWorkspaceMember,
)
from .serializers import (
    AddProjectMemberSerializer,
    BoardSerializer,
    ProjectMemberSerializer,
    ProjectSerializer,
    TaskSerializer,
)


@extend_schema(
    tags=['Projects'],
    summary='Список и создание проектов',
    description='Возвращает проекты workspace. Для создания необходима роль администратора workspace.',
)
class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]  # noqa: RUF012

    def get_queryset(self):
        workspace_id = self.kwargs.get('workspace_id')
        user = self.request.user

        return Project.objects.filter(
            workspace_id=workspace_id,
            workspace__memberships__user=user
        ).distinct()

    def perform_create(self, serializer):
        workspace_id = self.kwargs.get('workspace_id')
        workspace = get_object_or_404(
            Workspace,
            id=workspace_id
        )

        if not Membership.objects.filter(
                workspace=workspace,
                user=self.request.user,
                role='admin'
        ).exists():
            raise PermissionDenied("Только администратор рабочего пространства может создавать проекты")

        project = serializer.save(workspace=workspace, owner=self.request.user)

        ProjectMember.objects.create(project=project, user=self.request.user, role='admin')


@extend_schema(
    tags=['Projects'],
    summary='Детали, обновление, удаление проекта',
    description='Просмотр, изменение и удаление проекта. Только администраторы проекта или workspace.',
)
class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsWorkspaceMember, IsProjectOwnerOrAdmin]  # noqa: RUF012
    queryset = Project.objects.all()

    def perform_update(self, serializer):
        project = self.get_object()

        if not (ProjectMember.objects.filter(project=project,
                                             user=self.request.user,
                                             role='admin').exists()):
            raise PermissionError("У вас недостаточно прав для редактирования этого проекта")

        serializer.save()

    def perform_destroy(self, instance):
        if not (ProjectMember.objects.filter(project=instance,
                                             user=self.request.user,
                                             role='admin').exists()):
            raise PermissionError("У вас недостаточно прав для удаления этого проекта")

        instance.delete()


@extend_schema(
    tags=['Projects'],
    summary='Добавить участника проекта',
    description='Добавляет существующего пользователя в проект. Требует права администратора проекта или workspace.',
)
class ProjectMemberCreateView(generics.CreateAPIView):
    serializer_class = AddProjectMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        project_id = self.kwargs.get('project_id')
        context['project'] = get_object_or_404(Project, id=project_id)
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = self.get_serializer_context()['project']

        if not (ProjectMember.objects.filter(project=project,
                                             user=request.user,
                                             role='admin').exists()
                or
                Membership.objects.filter(workspace=project.workspace,
                                          user=request.user,
                                          role='admin').exists()):

            return Response({"detail": "Недостаточно прав для добавления участников"},
                            status=status.HTTP_403_FORBIDDEN)

        self.perform_create(serializer)

        output_serializer = ProjectMemberSerializer(serializer.instance)

        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=['Boards'],
    summary='Список и создание досок',
    description='Возвращает доски проекта. Создавать доски могут администраторы проекта или workspace.',
)
class BoardListCreateView(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated]  # noqa: RUF012

    def get_queryset(self):
        project_id = self.kwargs['project_id']

        return Board.objects.filter(
            project_id=project_id,
            project__members__user=self.request.user
        ).distinct()

    def perform_create(self, serializer):
        project = get_object_or_404(Project, id=self.kwargs['project_id'])

        if not (ProjectMember.objects.filter(project=project, user=self.request.user, role='admin').exists() or
                Membership.objects.filter(workspace=project.workspace, user=self.request.user, role='admin').exists()):
            raise PermissionDenied("Только администратор может создавать доски")

        board = serializer.save(project=project, owner=self.request.user)

        send_workspace_notification(project.workspace_id, {
            'action': 'board_created',
            'board_id': board.id,
            'board_name': board.name,
            'project_id': project.id
        })


@extend_schema(
    tags=['Boards'],
    summary='Детали, обновление, удаление доски',
    description='Просмотр, изменение и удаление доски. Только администраторы проекта или workspace.',
)
class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]  # noqa: RUF012
    queryset = Board.objects.all()

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [permissions.IsAuthenticated(), IsProjectAdmin()]

        return [permissions.IsAuthenticated(), IsProjectMember()]


@extend_schema(
    tags=['Tasks'],
    summary='Список и создание задач',
    description='Возвращает задачи на доске. Создавать задачи могут администраторы проекта или workspace.',
)
class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]  # noqa: RUF012

    def get_queryset(self):
        board_id = self.kwargs['board_id']

        return Task.objects.filter(
            board_id=board_id,
            board__project__members__user=self.request.user
        ).distinct()

    def perform_create(self, serializer):
        board = get_object_or_404(Board, id=self.kwargs['board_id'])
        project = board.project

        if not (ProjectMember.objects.filter(project=project, user=self.request.user, role='admin').exists() or
                Membership.objects.filter(workspace=project.workspace, user=self.request.user, role='admin').exists()):
            raise PermissionDenied("Только администратор может создавать задачи")

        task = serializer.save(board=board, created_by=self.request.user)

        send_workspace_notification(project.workspace_id, {
            'action': 'task_created',
            'task_id': task.id,
            'title': task.title,
            'status': task.status,
            'priority': task.priority,
            'executor_id': task.executor_id
        })


@extend_schema(
    tags=['Tasks'],
    summary='Детали, обновление, удаление задачи',
    description='Просмотр и изменение задачи. При обновлении отправляется WebSocket-уведомление. Удаление – только администраторам.',
)
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]  # noqa: RUF012
    queryset = Task.objects.all()

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [permissions.IsAuthenticated(), IsProjectAdmin()]

        return [permissions.IsAuthenticated(), IsProjectMember()]

    def perform_update(self, serializer):
        task = serializer.save()
        send_workspace_notification(task.board.project.workspace_id, {
            'action': 'task_updated',
            'task_id': task.id,
            'title': task.title,
            'status': task.status,
            'priority': task.priority,
            'executor_id': task.executor_id
        })
