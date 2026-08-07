from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from accounts.models import User

from .models import Invitation, Membership, Workspace
from .permissions import IsOwnerOrAdmin
from .serializers import (
    AddMemberSerializer,
    InvitationSerializer,
    MembershipSerializer,
    WorkspaceSerializer,
)


@extend_schema(
    tags=['Workspaces'],
    summary='Список и создание рабочих пространств',
    description='Возвращает пространства, где пользователь участник или владелец. Для создания нужно быть аутентифицированным.',
)
class WorkspaceListCreateView(generics.ListCreateAPIView):
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]  # noqa: RUF012

    def get_queryset(self):
        return Workspace.objects.filter(memberships__user=self.request.user)

    def perform_create(self, serializer):
        workspace = serializer.save(owner=self.request.user)
        Membership.objects.create(
            workspace=workspace,
            user=self.request.user,
            role='admin'
        )


@extend_schema(
    tags=['Workspaces'],
    summary='Детали, удаление рабочего пространства',
    description='Просмотр и удаление пространства. Только владелец или администратор.',
)
class WorkspaceDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]  # noqa: RUF012
    queryset = Workspace.objects.all()


@extend_schema(
    tags=['Workspaces'],
    summary='Добавить существующего пользователя',
    description='Добавляет зарегистрированного пользователя в рабочее пространство. Требует права администратора workspace.',
)
class MembershipCreateView(generics.CreateAPIView):
    serializer_class = AddMemberSerializer
    permission_classes = [permissions.IsAuthenticated]  # noqa: RUF012

    def get_serializer_context(self):
        context = super().get_serializer_context()
        workspace_id = self.kwargs.get("workspace_id")
        context["workspace"] = get_object_or_404(Workspace, id=workspace_id)

        return context


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workspace = self.get_serializer_context()["workspace"]
        if not (Membership.objects.filter(workspace=workspace,
                                          user=request.user,
                                          role="admin").exists()):
            return Response({"detail": "Недостаточно прав"},
                            status=status.HTTP_403_FORBIDDEN)

        self.perform_create(serializer)
        membership = serializer.instance

        output_serializer = MembershipSerializer(membership)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=['Workspaces'],
    summary='Создать приглашение',
    description='Создаёт приглашение для нового участника (по email). Отправляет письмо со ссылкой. Доступно администраторам.',
)
class InvitationCreateView(generics.CreateAPIView):
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]  # noqa: RUF012

    def get_serializer_context(self):
        context = super().get_serializer_context()
        workspaces_id = self.kwargs.get("workspace_id")
        context["workspace"] = get_object_or_404(Workspace, id=workspaces_id)

        return context

    def perform_create(self, serializer):
        workspace = self.get_serializer_context()["workspace"]
        if not (Membership.objects.filter(workspace=workspace,
                                  user=self.request.user,
                                  role="admin").exists()
        ):
            raise PermissionError("Недостаточно прав")

        invitation = serializer.save()
        invitation.send_invitation_email()


@extend_schema(
    tags=['Workspaces'],
    summary='Принять приглашение',
    description='Активирует приглашение по токену. Если пользователь новый, создаёт его (требуется пароль). Добавляет в workspace.',
)
class AcceptInvitationView(generics.GenericAPIView):
    def post(self, request, token):
        invitation = get_object_or_404(Invitation, token=token, accepted=False)
        email = invitation.email
        password = request.data.get("password")

        user, created = User.objects.get_or_create(email=email)
        if created:
            if not password:
                return Response(
                    {"detail": "Пароль обязателен для нового пользователя"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(password)
            user.save()

        Membership.objects.get_or_create(
            workspace=invitation.workspace,
            user=user,
            defaults={"role": "member"}
        )

        invitation.accepted = True
        invitation.save()

        Invitation.objects.filter(
            workspace=invitation.workspace,
            email=email,
            accepted=False
        ).update(accepted=True)

        return Response({"detail": "Приглашение принято. Вы добавлены в рабочее пространство"})
