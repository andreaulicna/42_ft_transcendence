
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    #re_path(r'^api/matchmaking/ws/(?P<uuid>[0-9a-f-]+)/$', consumers.MatchmakingConsumer.as_asgi()),
    re_path(r'^api/matchmaking/ws/$', consumers.MatchmakingConsumer.as_asgi()),
]