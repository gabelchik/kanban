from django.template.defaultfilters import add
from rest_framework import serializers
from .models import Workspace, Membership, Invitation
from accounts.models import User


class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Membership
        fields = ("id", "user", "user_email", "role", "joined_at")
        read_only_fields = ("user", "joined_at")


class AddMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=Membership.ROLE_CHOICES, default="member")

    def validate_email(self, value):
        workspace = self.context["workspace"]
        user = User.objects.filter(email=value).first()
        if not user:
            raise serializers.ValidationError("Пользователь с таким email не найден")
        if Membership.objects.filter(workspace=workspace, user=user).exists():
            raise serializers.ValidationError("Пользователь уже является участником")

        return value

    def create(self, validated_data):
        workspace = self.context["workspace"]
        user = User.objects.get(email=validated_data["email"])
        membership = Membership.objects.create(
            workspace=workspace,
            user=user,
            role=validated_data["role"]
        )

        return membership

class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ("id", "email", "created_at", "accepted")
        read_only_fields = ("created_at", "accepted")

    def validate_email(self, value):
        workspace = self.context["workspace"]
        user = User.objects.filter(email=value).first()
        if user:
            if Membership.objects.filter(workspace=workspace, user=user).exists():
                raise serializers.ValidationError("Пользователь уже является участником")
            raise serializers.ValidationError(
                "Этот пользователь уже зарегистрирован. Добавьте его напрямую через /members/.")

        return value

    def create(self, validated_data):
        workspace = self.context["workspace"]
        email = validated_data["email"]
        invitation = Invitation.objects.create(workspace=workspace, email=email)

        return invitation


class WorkspaceSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    members = MembershipSerializer(source="memberships", many=True, read_only=True)

    class Meta:
        model = Workspace
        fields = ("id", "name", "description", "owner", "owner_email", "created_at", "members")
        read_only_fields = ("owner", "created_at")
