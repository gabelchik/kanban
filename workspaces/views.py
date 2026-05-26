from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Workspaces, MemberShip
from accounts.models import User
from .serializers import WorkspaceSerializer, MembershipSerializer
from .permissions import IsOwnerOrAdmin


class WorkspaceListCreateView(generics.ListCreateAPIView):
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Workspaces.objects.filter(
            Q(owner=user) | Q(memberships__user=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class WorkspaceDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    queryset = Workspaces.objects.all()


class MembershipCreateView(generics.CreateAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        workspace_id = self.kwargs.get("workspace_id")
        workspace = Workspaces.objects.get(id=workspace_id)

        if not (request.user == workspace.owner or
        MemberShip.objects.filter(
            workspace=workspace,
            user=request.user,
            role="admin"
        ).exists()):
            return Response({"detail": "Недостаточно прав"},
                            status=status.HTTP_403_FORBIDDEN)

        email = request.data.get("email")
        role = request.data.get("role", "member")
        user = User.objects.get(email=email)
        if MemberShip.objects.filter(workspace=workspace, user=user).exists():
            return Response(
                {"detail": "Пользователь уже участник"},
                status=status.HTTP_400_BAD_REQUEST
            )

        membership = MemberShip.objects.create(workspace=workspace, user=user, role=role)
        serializer = self.get_serializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
