
from django.urls import re_path
from . import consumers

print('hello authentication');
websocket_urlpatterns = [
    re_path(r'^api/auth/ws/init/$', consumers.UserConsumer.as_asgi()),
]