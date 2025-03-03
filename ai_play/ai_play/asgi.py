"""
ASGI config for ai_play project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_play.settings')
django_asgi_app = get_asgi_application()

from django_channels_jwt.middleware import JwtAuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import api.routing


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JwtAuthMiddlewareStack(
        URLRouter(
            api.routing.websocket_urlpatterns
        )
    ),
})