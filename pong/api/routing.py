
from django.urls import re_path
from . import consumers

print('hello pong');
websocket_urlpatterns = [
    re_path(r'^api/pong/ws/(?P<uuid>[0-9a-f-]+)/$', consumers.PongConsumer.as_asgi()),
    re_path(r'^api/pong/ws/$', consumers.PongConsumer.as_asgi()),
]