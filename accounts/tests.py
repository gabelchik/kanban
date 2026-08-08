import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from tests.factories import UserFactory


@pytest.mark.django_db
class TestAuth:
    def setup_method(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.token_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')

    def test_register_user(self):
        """Успешная регистрация нового пользователя."""
        data = {'email': 'new@example.com', 'password': 'strongpass123'}
        response = self.client.post(self.register_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email='new@example.com').exists()

    def test_register_missing_email(self):
        """Ошибка при отсутствии email."""
        data = {'password': 'strongpass123'}
        response = self.client.post(self.register_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_obtain_token(self):
        """Успешное получение JWT пары."""
        user = UserFactory()
        data = {'email': user.email, 'password': 'strongpass123'}
        response = self.client.post(self.token_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_refresh_token(self):
        """Обновление access токена по refresh токену."""
        user = UserFactory()
        resp = self.client.post(self.token_url, {'email': user.email, 'password': 'strongpass123'})
        refresh = resp.data['refresh']
        response = self.client.post(self.refresh_url, {'refresh': refresh})
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
