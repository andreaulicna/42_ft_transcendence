from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import CustomUser

@database_sync_to_async
def identify_player_by_id(id):
	return CustomUser.objects.get(id=id)

class UserConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		await self.accept()
		self.id = self.scope['user'].id
		
	async def disconnect(self, close_code):
		print("Goodbye world")