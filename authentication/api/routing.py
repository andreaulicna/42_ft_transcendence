
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path("auth/ws/login/", consumers.UserConsumer.as_asgi()),
]