from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import uuid # unique room_id
from pprint import pprint # nice printing
from channels.db import database_sync_to_async
from .models import WebSocketTicket

rooms = []

def create_room():
	room = {
		"players": [],
		'room_id': str(uuid.uuid4()),
	}
	rooms.append(room)
	return room

def add_player_to_room(room, player_id, channel_name):
	room['players'].append({player_id: channel_name})

def find_room_to_join():
	for room in rooms:
		if len(room['players']) < 2:
			return room
	return None

def get_user_by_uuid(uuid):
	try:
		print("Validating against database")
		ticket_uuid = WebSocketTicket.objects.get(uuid=uuid)
		return ticket_uuid.user
	except WebSocketTicket.DoesNotExist:
		return None

class MatchmakingConsumer(WebsocketConsumer):
	def connect(self):
		# this part is for validating it against the database
		self.uuid = self.scope['url_route']['kwargs']['uuid']
		self.user = get_user_by_uuid(self.uuid)

		if self.user is None:
			print("User is NONE")
			self.close()
			return

		self.id = self.user.id
		print(f"Player {self.id} wants to play match a match!")
		room = find_room_to_join()
		if not room:
			room = create_room()
		add_player_to_room(room, self.id, self.channel_name)
		self.room_group_name = room['room_id']
		async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
		self.accept()
		print("Rooms after accept:")
		pprint(rooms)

	def disconnect(self, close_code):
		for room in rooms:
			for player in room['players']:
				if self.channel_name in player.values():
					async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)
					room['players'].remove(player)
					if not room['players']:
						rooms.remove(room)
					break
		print("Rooms after disconnect:")
		pprint(rooms)