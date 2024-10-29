
from django.urls import re_path
from . import consumers

print('hello authentication');
websocket_urlpatterns = [
    re_path(r'^api/auth/ws/init/(?P<uuid>[0-9a-f-]+)/$', consumers.UserConsumer.as_asgi()),
    re_path(r'^api/auth/ws/init/$', consumers.UserConsumer.as_asgi()),
]