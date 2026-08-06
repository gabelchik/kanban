from rest_framework import serializers

from accounts.models import User

from .models import Board, Project, ProjectMember, Task


class ProjectMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMember
        fields = ('id', 'user', 'user_email', 'role', 'joined_at')
        read_only_fields = ('joined_at',)

    user_email = serializers.EmailField(source='user.email', read_only=True)


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'workspace', 'owner', 'owner_email',
                  'created_at', 'is_active', 'members')
        read_only_fields = ('owner', 'created_at', 'workspace')

    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    members = ProjectMemberSerializer(many=True, read_only=True)


class AddProjectMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=ProjectMember.ROLE_CHOICES, default='member')

    def validate_email(self, value):
        project = self.context['project']

        user = User.objects.filter(email=value).first()
        if not user:
            raise serializers.ValidationError("Пользователь с таким email не найден.")

        if ProjectMember.objects.filter(project=project, user=user).exists():
            raise serializers.ValidationError("Пользователь уже является участником проекта.")

        if not project.workspace.memberships.filter(user=user).exists():
            raise serializers.ValidationError("Пользователь не является участником рабочего пространства.")

        return value

    def create(self, validated_data):
        project = self.context['project']
        user = User.objects.get(email=validated_data['email'])
        return ProjectMember.objects.create(
            project=project,
            user=user,
            role=validated_data['role']
        )


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'priority',
                  'executor', 'executor_email', 'created_by', 'created_by_email',
                  'order', 'created_at', 'updated_at')
        read_only_fields = ('created_by', 'created_at', 'updated_at')

    executor_email = serializers.EmailField(source='executor.email', read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ('id', 'name', 'description', 'project', 'owner', 'owner_email',
                  'created_at', 'tasks')
        read_only_fields = ('owner', 'created_at', 'project')

    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
