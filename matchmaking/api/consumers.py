from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import uuid # unique room_id
from pprint import pprint # nice printing
from .models import CustomUser, Match
import json
from .serializers import MatchSerializer

rooms = []

def create_room():
	room = {
		'players': [],
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

def is_player_in_room_already(player_id):
	for room in rooms:
		for player in room['players']:
			if player_id in player:
				return True
	return False

def get_player_state(player_id):
	try:
		user = CustomUser.objects.get(id=player_id)
		return user.state
	except CustomUser.DoesNotExist:
		return None
	
def set_user_to_ingame(player_id):
	user = CustomUser.objects.get(id=player_id)
	user.state = CustomUser.StateOptions.INGAME
	user.save(update_fields=["state"])

class MatchmakingConsumer(WebsocketConsumer):
	def connect(self):
		self.id = self.scope['user'].id
		print(f"Player {self.id} wants to play a match!")
		if is_player_in_room_already(self.id) or get_player_state(self.id) in (CustomUser.StateOptions.INGAME, CustomUser.StateOptions.INTOURNAMENT):
			self.close()
			return 
		room = find_room_to_join()
		if not room:
			room = create_room()
		add_player_to_room(room, self.id, self.channel_name)
		self.room_group_name = room['room_id']
		async_to_sync(self.channel_layer.group_add)(
			self.room_group_name, self.channel_name
		)
		self.accept()
		if len(room['players']) == 2:
			data = {
				'player1' : list(room['players'][0].keys())[0],
				'player2' : list(room['players'][1].keys())[0]
			}
			match_serializer = MatchSerializer(data=data)
			if match_serializer.is_valid():
				match_serializer.save()
				set_user_to_ingame(list(room['players'][0].keys())[0])
				set_user_to_ingame(list(room['players'][1].keys())[0])
				async_to_sync(self.channel_layer.group_send)(
					self.room_group_name, {"type": "matchmaking_message", "message": match_serializer.data['id']}
				)
				print("Rooms after connect:")
				pprint(rooms)
		print("Rooms after connect:")
		pprint(rooms)

	def disconnect(self, close_code):
		for room in rooms:
			for player in room['players']:
				if self.channel_name in player.values():
					async_to_sync(self.channel_layer.group_discard)(
						self.room_group_name, self.channel_name
					)
					room['players'].remove(player)
					if not room['players']:
						rooms.remove(room)
					break
		print("Rooms after disconnect:")
		pprint(rooms)
	
	def receive(self, text_data):
		text_data_json = json.loads(text_data)
		message = text_data_json["message"]
		print(f"Message in receive: {message}")

		# Send message to room group
		async_to_sync(self.channel_layer.group_send)(
			self.room_group_name, {"type": "matchmaking_message", "message": message}
		)
	
	def matchmaking_message(self, event):
		message = event["message"]
		print(f"Received group message: {message}")
		self.send(text_data=json.dumps({"message": message}))
		self.close()