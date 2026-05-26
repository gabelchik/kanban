from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .models import Workspace, Membership, Invitation
from accounts.models import User
from .permissions import IsOwnerOrAdmin

from .serializers import (
    WorkspaceSerializer,
    InvitationSerializer,
    AddMemberSerializer,
    MembershipSerializer,
)


class WorkspaceListCreateView(generics.ListCreateAPIView):
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Workspace.objects.filter(
            Q(owner=user) | Q(memberships__user=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class WorkspaceDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    queryset = Workspace.objects.all()


class MembershipCreateView(generics.CreateAPIView):
    serializer_class = AddMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        workspace_id = self.kwargs.get("workspace_id")
        context["workspace"] = get_object_or_404(Workspace, id=workspace_id)

        return context


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workspace = self.get_serializer_context()["workspace"]
        if not (request.user == workspace.owner or
                Membership.objects.filter(workspace=workspace,
                                          user=request.user,
                                          role="admin").exists()):
            return Response({"detail": "Недостаточно прав"},
                            status=status.HTTP_403_FORBIDDEN)

        self.perform_create(serializer)
        membership = serializer.instance

        output_serializer = MembershipSerializer(membership)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class InvitationCreateView(generics.CreateAPIView):
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        workspaces_id = self.kwargs.get("workspace_id")
        context["workspace"] = get_object_or_404(Workspace, id=workspaces_id)

        return context

    def perform_create(self, serializer):
        workspace = self.get_serializer_context()["workspace"]
        if not (self.request.user == workspace.owner or
        Membership.objects.filter(workspace=workspace,
                                  user=self.request.user,
                                  role="admin").exists()
        ):
            raise PermissionError("Недостаточно прав")

        invitation = serializer.save()
        invitation.send_invitation_email()


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