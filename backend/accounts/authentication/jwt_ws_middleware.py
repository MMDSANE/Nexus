# accounts/authentication/jwt_ws_middleware.py

from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from django.db import close_old_connections
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError


User = get_user_model()


class JWTAuthMiddleware(BaseMiddleware):

    async def __call__(self, scope, receive, send):
        close_old_connections()

        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)

        token = query_params.get("token")

        if token:
            try:
                access_token = AccessToken(token[0])
                user = await self.get_user(access_token["user_id"])
                scope["user"] = user
            except TokenError:
                scope["user"] = None
        else:
            scope["user"] = None

        return await super().__call__(scope, receive, send)

    @staticmethod
    async def get_user(user_id):
        try:
            return await User.objects.aget(id=user_id)
        except User.DoesNotExist:
            return None

def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(inner)