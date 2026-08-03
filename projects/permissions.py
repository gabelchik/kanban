from rest_framework import permissions

from workspaces.models import Membership

from .models import ProjectMember


class IsWorkspaceMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return True  # Пропускаем, основная фильтрация в get_queryset

    def has_object_permission(self, request, view, obj):
        workspace = obj.workspace
        return Membership.objects.filter(
            workspace=workspace,
            user=request.user
        ).exists()


class IsProjectOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return ProjectMember.objects.filter(
            project=obj,
            user=request.user,
            role='admin'
        ).exists()
