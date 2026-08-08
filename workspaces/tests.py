import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tests.factories import UserFactory, WorkspaceFactory
from workspaces.models import Membership, Workspace


@pytest.mark.django_db
class TestWorkspaces:
    def setup_method(self):
        self.client = APIClient()
        self.owner = UserFactory()
        response = self.client.post(
            reverse('token_obtain_pair'),
            {'email': self.owner.email, 'password': 'strongpass123'}
        )
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.list_create_url = reverse('workspace-list')
        self.detail_url = lambda pk: reverse('workspace-detail', kwargs={'pk': pk})

    def test_create_workspace(self):
        """Создание рабочего пространства и автоматическое членство владельца как admin."""
        data = {'name': 'Test workspace', 'description': 'desc'}
        response = self.client.post(self.list_create_url, data)
        assert response.status_code == status.HTTP_201_CREATED

        workspace = Workspace.objects.first()
        assert Membership.objects.filter(
            workspace=workspace, user=self.owner, role='admin'
        ).exists()

    def test_list_workspaces(self):
        """Список показывает только пространства, принадлежащие владельцу."""
        workspace1 = WorkspaceFactory(owner=self.owner)
        workspace2 = WorkspaceFactory(owner=self.owner)

        workspace_other = WorkspaceFactory()

        response = self.client.get(self.list_create_url)
        assert response.status_code == status.HTTP_200_OK

        ids = [w['id'] for w in response.data]
        assert workspace1.id in ids and workspace2.id in ids
        assert workspace_other.id not in ids

    def test_workspace_detail(self):
        """Просмотр деталей пространства владельцем."""
        workspace = WorkspaceFactory(owner=self.owner)
        response = self.client.get(self.detail_url(workspace.id))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == workspace.name
