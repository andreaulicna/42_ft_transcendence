from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import CustomUser, WebSocketTicket

#{
# 'type': 'websocket', 
# 'path': '/api/auth/ws/login/consume/', 
# 'raw_path': b'/api/auth/ws/login/consume/', 
# 'root_path': '', 
# 'headers': [(b'upgrade', b'websocket'), (b'connection', b'upgrade'), (b'x-forwarded-for', b'192.168.65.1'), (b'host', b'localhost:1337'), (b'sec-websocket-version', b'13'), (b'sec-websocket-key', b'oz8cxW2v8gTJHQqN6Nh6Mg=='), (b'sec-websocket-extensions', b'permessage-deflate; client_max_window_bits')], 
# 'query_string': b'uuid=6145c83c-d2ce-49e8-934b-1b83a26c65ca', 
# 'client': ['172.18.0.7', 34330], 
# 'server': ['172.18.0.3', 9000], 
# 'subprotocols': [], 
# 'asgi': {'version': '3.0'}, 
# 'user': <CustomUser: testusr2>, 
# 'cookies': {}, 
# 'session': <django.utils.functional.LazyObject object at 0xffff96d59270>, 
# 'path_remaining': '', 
# 'url_route': {'args': (), 'kwargs': {}}}

# {'groups': [], 
# 'scope': ...
# 'channel_layer': None, 
# 'base_send': <bound method InstanceSessionWrapper.send of <channels.sessions.InstanceSessionWrapper object at 0xffffb8c2bd30>>, 
# 'id': 1}

@database_sync_to_async
def set_user_state(user, userState):
	user.state = userState
	user.save(update_fields=["state"])

@database_sync_to_async
def get_user_by_uuid(uuid):
	try:
		print("Validating against database")
		ticket_uuid = WebSocketTicket.objects.get(uuid=uuid)
		return ticket_uuid.user
	except WebSocketTicket.DoesNotExist:
		return None

class UserConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		await self.accept()
		self.id = self.scope['user'].id
		print(f"Player {self.id} says hello!")
		await set_user_state(self.scope['user'], CustomUser.StateOptions.ONLINE)

	async def disconnect(self, close_code):
		await set_user_state(self.scope['user'], CustomUser.StateOptions.OFFLINE)
		print(f"Player {self.id} says goodbye!")
