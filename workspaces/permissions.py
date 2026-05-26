from rest_framework import permissions
from workspaces.models import MemberShip


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.owner:
            return True
        return MemberShip.objects.filter(workspace=obj, user=request.user, role="admin").exists()