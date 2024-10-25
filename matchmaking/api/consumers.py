from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

rooms = []

class MatchmakingConsumer(WebsocketConsumer):
	def connect(self):
		self.accept()
		for room in rooms:
			if (len(room) < 2):
				async_to_sync(self.channel_layer.group_add(room, self.channel_name))

	def disconnect(self, close_code):
		# find the room the consumer is in and delete it from there