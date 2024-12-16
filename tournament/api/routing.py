
from django.urls import re_path
from . import consumers

print('hello tournament');
websocket_urlpatterns = [
    re_path(r'^api/ws/tournament/(?P<tournament_id>\d+)/$', consumers.TournamentConsumer.as_asgi()),
]