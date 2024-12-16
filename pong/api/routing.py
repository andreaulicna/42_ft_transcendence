
from django.urls import re_path
from . import consumers

print('hello pong');
websocket_urlpatterns = [
    re_path(r'^api/ws/pong/(?P<match_id>\d+)/$', consumers.PongConsumer.as_asgi()),
]