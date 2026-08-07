from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import User
from .serializers import RegisterSerializer


@extend_schema(
    tags=['Auth'],
    summary='Регистрация',
    description='Создаёт нового пользователя с указанными email и паролем.',
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

@extend_schema(
    tags=['Auth'],
    summary='Получение JWT токенов',
    description='Принимает email и пароль, возвращает refresh и access токены.',
)
class CustomTokenObtainPairView(TokenObtainPairView):
    pass

@extend_schema(
    tags=['Auth'],
    summary='Обновление access токена',
    description='Принимает refresh токен и возвращает новый access токен.',
)
class CustomTokenRefreshView(TokenRefreshView):
    pass