from rest_framework import permissions
from workspaces.models import Membership


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.owner:
            return True
        return Membership.objects.filter(workspace=obj, user=request.user, role="admin").exists()