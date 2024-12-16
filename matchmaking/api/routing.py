
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^api/ws/matchmaking/$', consumers.MatchmakingConsumer.as_asgi()),
    re_path(r'^api/ws/matchmaking/(?P<prev_match_id>\d+)/rematch/$', consumers.RematchConsumer.as_asgi()),
]