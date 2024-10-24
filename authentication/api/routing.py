
from django.urls import path
from . import consumers

print('hello');
websocket_urlpatterns = [
    path("api/auth/ws/login/consume/", consumers.UserConsumer.as_asgi()),
]