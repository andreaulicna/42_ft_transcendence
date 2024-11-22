
from django.urls import re_path
from . import consumers

print('hello pong');
websocket_urlpatterns = [
    re_path(r'^api/tournament/ws/(?P<capacity>\d+)/$', consumers.TournamentConsumer.as_asgi()),
]