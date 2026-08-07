from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware


@database_sync_to_async
def get_user(token_str):
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import AnonymousUser
    from rest_framework_simplejwt.tokens import AccessToken

    try:
        access_token = AccessToken(token_str)
        User = get_user_model()

        return User.objects.get(id=access_token['user_id'])

    except Exception:  # noqa: BLE001
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        from django.contrib.auth.models import AnonymousUser

        query_string = scope.get('query_string', b'').decode()
        params = dict(p.split('=') for p in query_string.split('&') if '=' in p)

        token = params.get('token')
        scope['user'] = await get_user(token) if token else AnonymousUser()

        return await super().__call__(scope, receive, send)
