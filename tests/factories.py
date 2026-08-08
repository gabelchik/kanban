import factory

from accounts.models import User
from projects.models import Board, Project, Task
from workspaces.models import Workspace


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.PostGenerationMethodCall('set_password', 'strongpass123')


class WorkspaceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Workspace

    name = factory.Sequence(lambda n: f"Workspace {n}")
    description = factory.Faker('sentence')
    owner = factory.SubFactory(UserFactory)

    @factory.post_generation
    def add_owner_as_admin(self, create, extracted, **kwargs):
        if not create:
            return
        from workspaces.models import Membership
        Membership.objects.get_or_create(
            workspace=self,
            user=self.owner,
            defaults={'role': 'admin'}
        )


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Sequence(lambda n: f"Project {n}")
    description = factory.Faker('sentence')
    workspace = factory.SubFactory(WorkspaceFactory)
    owner = factory.SubFactory(UserFactory)

    @factory.post_generation
    def add_owner_as_admin(self, create, extracted, **kwargs):
        if not create:
            return
        from projects.models import ProjectMember
        ProjectMember.objects.get_or_create(
            project=self,
            user=self.owner,
            defaults={'role': 'admin'}
        )


class BoardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Board

    name = factory.Sequence(lambda n: f"Board {n}")
    description = factory.Faker('sentence')
    project = factory.SubFactory(ProjectFactory)
    owner = factory.SubFactory(UserFactory)


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Sequence(lambda n: f"Task {n}")
    description = factory.Faker('sentence')
    board = factory.SubFactory(BoardFactory)
    created_by = factory.SubFactory(UserFactory)
    # status, priority, order – по умолчанию из модели (backlog, medium, 0)