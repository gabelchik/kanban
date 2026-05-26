from rest_framework import serializers
from .models import Workspaces, MemberShip


class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = MemberShip
        fields = ("id", "user", "user_email", "role", "joined_at")
        read_only_fields = ("user", "joined_at")


class WorkspaceSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    members = MembershipSerializer(source="memberships", many=True, read_only=True)

    class Meta:
        model = Workspaces
        fields = ("id", "name", "description", "owner", "owner_email", "created_at", "members")
        read_only_fields = ("owner", "created_at")
