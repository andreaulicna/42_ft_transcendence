
from django.urls import re_path
from . import consumers

print('hello localplay');
websocket_urlpatterns = [
    re_path(r'^api/ws/localplay/(?P<match_id>\d+)/$', consumers.LocalPlayConsumer.as_asgi()),
]