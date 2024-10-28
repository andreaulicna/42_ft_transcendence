"""
ASGI config for matchmaking project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'matchmaking.settings')
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from django_channels_jwt.middleware import JwtAuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import api.routing


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(	# temporary removed authentication to code the logic
        URLRouter(
            api.routing.websocket_urlpatterns
        )
	),
})