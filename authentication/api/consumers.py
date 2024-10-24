from channels.generic.websocket import AsyncWebsocketConsumer
import jwt


class UserConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		print("Hello world")
		await self.accept()