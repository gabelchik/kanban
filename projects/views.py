from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

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

        serializer.save(project=project, owner=self.request.user)

class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]  # noqa: RUF012
    queryset = Board.objects.all()

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [permissions.IsAuthenticated(), IsProjectAdmin()]

        return [permissions.IsAuthenticated(), IsProjectMember()]

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

        serializer.save(board=board, created_by=self.request.user)

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]  # noqa: RUF012
    queryset = Task.objects.all()

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [permissions.IsAuthenticated(), IsProjectAdmin()]

        return [permissions.IsAuthenticated(), IsProjectMember()]
