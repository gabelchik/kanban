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


class IsProjectMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        project = obj.board.project if hasattr(obj, 'board') else obj.project
        user = request.user

        if ProjectMember.objects.filter(project=project, user=user).exists():
            return True

        return bool(Membership.objects.filter(workspace=project.workspace, user=user, role='admin').exists())

class IsProjectAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        project = obj.board.project if hasattr(obj, 'board') else obj.project
        user = request.user

        if ProjectMember.objects.filter(project=project, user=user, role='admin').exists():
            return True

        return bool(Membership.objects.filter(workspace=project.workspace, user=user, role='admin').exists())
