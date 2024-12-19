
from django.urls import re_path
from . import consumers

print('hello ai_play');
websocket_urlpatterns = [
    re_path(r'^api/ws/ai/(?P<match_id>\d+)/$', consumers.AIPlayConsumer.as_asgi()),
]