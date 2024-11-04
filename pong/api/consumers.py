from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import CustomUser

@database_sync_to_async
def set_user_state(user, userState):
	user.state = userState
	user.save(update_fields=["state"])

class PongConsumer(AsyncWebsocketConsumer):
	# just placeholder code to see if the connect/ disconnect works
	async def connect(self):
		self.id = self.scope['user'].id
		print(f"Player {self.id} is ready to play pong!")
		await set_user_state(self.scope['user'], CustomUser.StateOptions.INGAME)
		await self.accept()

	async def disconnect(self, close_code):
		await set_user_state(self.scope['user'], CustomUser.StateOptions.ONLINE)
		print(f"Player {self.id} is done playing pong!")