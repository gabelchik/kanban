import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from projects.models import Board, Project, ProjectMember, Task
from tests.factories import BoardFactory, ProjectFactory, UserFactory, WorkspaceFactory


@pytest.mark.django_db
class TestProjects:
    def setup_method(self):
        self.client = APIClient()
        self.owner = UserFactory()
        self.workspace = WorkspaceFactory(owner=self.owner)

        response = self.client.post(
            reverse('token_obtain_pair'),
            {'email': self.owner.email, 'password': 'strongpass123'}
        )
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_create_project(self):
        """Администратор workspace может создавать проекты и становится их админом."""
        url = reverse('project-list', kwargs={'workspace_id': self.workspace.id})
        data = {'name': 'New Project', 'description': 'test'}
        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED

        project = Project.objects.get(id=response.data['id'])
        assert project.workspace == self.workspace
        assert project.owner == self.owner
        assert ProjectMember.objects.filter(
            project=project, user=self.owner, role='admin'
        ).exists()

    def test_create_board(self):
        """Администратор проекта может создать доску."""
        project = ProjectFactory(workspace=self.workspace, owner=self.owner)

        url = reverse('board-list', kwargs={'project_id': project.id})
        data = {'name': 'New Board', 'description': 'board desc'}
        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Board.objects.filter(name='New Board', project=project).exists()

    def test_create_task(self):
        """Администратор проекта может создать задачу."""
        board = BoardFactory(project__workspace=self.workspace, owner=self.owner)

        url = reverse('task-list', kwargs={'board_id': board.id})
        data = {'title': 'Important Task', 'status': 'todo', 'priority': 'high'}
        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        task = Task.objects.get(title='Important Task')
        assert task.board == board
        assert task.created_by == self.owner

    def test_non_admin_cannot_create_project(self):
        """Обычный участник workspace (не admin) не может создать проект."""
        member = UserFactory()
        from workspaces.models import Membership
        Membership.objects.create(workspace=self.workspace, user=member, role='member')

        response = self.client.post(
            reverse('token_obtain_pair'),
            {'email': member.email, 'password': 'strongpass123'}
        )
        member_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {member_token}')

        url = reverse('project-list', kwargs={'workspace_id': self.workspace.id})
        data = {'name': 'Project by Member'}
        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
