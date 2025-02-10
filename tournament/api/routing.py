
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    #re_path(r'^api/ws/tournament/(?P<tournament_id>\d+)/$', consumers.TournamentConsumer.as_asgi()),
    re_path(r'^api/ws/tournament/local/(?P<local_tournament_id>\d+)/$', consumers.LocalTournamentConsumer.as_asgi()),
]