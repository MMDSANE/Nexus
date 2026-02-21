"""
ASGI config for Nexusmessenger project.
"""

import os
import django

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from accounts.authentication.jwt_ws_middleware import JWTAuthMiddlewareStack
from chat.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Nexusmessenger.settings")

django.setup()

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        # HTTP (Django / DRF)
        "http": django_asgi_app,

        # WebSocket (Channels)
        "websocket": JWTAuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),
    }
)