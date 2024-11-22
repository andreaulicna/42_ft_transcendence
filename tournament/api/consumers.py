from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import uuid # unique room_id
from pprint import pprint # nice printing
from .models import CustomUser, Match
import json
from .serializers import MatchSerializer

tournaments = []

def create_room(capacity):
	room = {
		'players': [],
		'room_id': str(uuid.uuid4()),
		'capacity': capacity
	}
	tournaments.append(room)
	return room

def add_player_to_room(room, player_id, channel_name):
	room['players'].append({player_id: channel_name})

def find_room_to_join():
	for room in tournaments:
		if len(room['players']) < room['capacity']:
			return room
	return None

def is_player_in_room_already(player_id):
	for room in tournaments:
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

def get_channel_name_by_player_id(room, player_id):
    for player in room['players']:
        if player_id in player:
            return player[player_id]
    return None

def get_player_id(room, index):
	return list(room['players'][index].keys())[0]

class TournamentConsumer(WebsocketConsumer):
	def connect(self):
		self.id = self.scope['user'].id
		capacity = int(self.scope['url_route']['kwargs'].get('capacity'))
		print(f"Player {self.id} wants to play a tournament with capacity {capacity}!")
		if is_player_in_room_already(self.id) or get_player_state(self.id) == CustomUser.StateOptions.INGAME:
			self.close()
			return 
		room = find_room_to_join()
		if not room:
			room = create_room(capacity)
		add_player_to_room(room, self.id, self.channel_name)
		self.room_group_name = room['room_id']
		async_to_sync(self.channel_layer.group_add)(
			self.room_group_name, self.channel_name
		)
		self.accept()
		if len(room['players']) == 4:
			# Get player ids
			player1_id = get_player_id(0)
			player2_id = get_player_id(1)
			player3_id = get_player_id(2)
			player4_id = get_player_id(3)
			# Create group_names for each round
			round1_group_name = "round1_" + room['room_id']
			round2_group_name = "round2_" + room['room_id']
			# Assign players to group_names for each round
			async_to_sync(self.channel_layer.group_add)(
				round1_group_name, get_channel_name_by_player_id(room, player1_id)
			)
			async_to_sync(self.channel_layer.group_add)(
				round1_group_name, get_channel_name_by_player_id(room, player2_id)
			)
			async_to_sync(self.channel_layer.group_add)(
				round2_group_name, get_channel_name_by_player_id(room, player3_id)
			)
			async_to_sync(self.channel_layer.group_add)(
				round2_group_name, get_channel_name_by_player_id(room, player4_id)
			)
			# Create math for round 1 and return match_id to players
			data1 = {
				'player1' : player1_id,
				'player2' : player2_id,
				'round' : 1
			}
			match_serializer1 = MatchSerializer(data=data1)
			if match_serializer1.is_valid():
				match_serializer1.save()
				async_to_sync(self.channel_layer.group_send)(
					round1_group_name, {"type": "tournament_message", "message": match_serializer1.data['id']}
				)
			# Create math for round 2 and return match_id to players
			data2 = {
				'player1' : player3_id,
				'player2' : player4_id,
				'round' : 2
			}
			match_serializer2 = MatchSerializer(data=data2)
			if match_serializer2.is_valid():
				match_serializer2.save()
				async_to_sync(self.channel_layer.group_send)(
					round2_group_name, {"type": "tournament_message", "message": match_serializer2.data['id']}
				)
		print("Tournaments after connect:")
		pprint(tournaments)

	def disconnect(self, close_code):
		for room in tournaments:
			for player in room['players']:
				if self.channel_name in player.values():
					async_to_sync(self.channel_layer.group_discard)(
						self.room_group_name, self.channel_name
					)
					room['players'].remove(player)
					if not room['players']:
						tournaments.remove(room)
					break
		print("Tournaments after disconnect:")
		pprint(tournaments)
	
	def receive(self, text_data):
		text_data_json = json.loads(text_data)
		message = text_data_json["message"]
		print(f"Message in receive: {message}")

		# Send message to room group
		async_to_sync(self.channel_layer.group_send)(
			self.room_group_name, {"type": "tournament_message", "message": message}
		)
	
	def tournament_message(self, event):
		message = event["message"]
		print(f"Received group message: {message}")
		self.send(text_data=json.dumps({"message": message}))
		self.close() # closes the websocket once the match_id has been sent to both of the players