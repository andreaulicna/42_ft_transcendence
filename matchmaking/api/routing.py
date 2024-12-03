
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^api/matchmaking/ws/$', consumers.MatchmakingConsumer.as_asgi()),
    re_path(r'^api/matchmaking/ws/(?P<prev_match_id>\d+)/rematch/$', consumers.RematchConsumer.as_asgi()),
]