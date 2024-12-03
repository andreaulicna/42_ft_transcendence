from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import uuid # unique room_id
from pprint import pprint # nice printing
from .models import CustomUser, Match
import json
from .serializers import MatchSerializer
from matchmaking.settings import GAME_CONSTANTS

rooms = []
rematch_rooms = []

class Player:
	def __init__(self, player_id, channel_name):
		self.id = player_id
		self.channel_name = channel_name

	def __repr__(self):
		return f"Player(id={self.id}, channel_name={self.channel_name})"

class MatchRoom:
	def __init__(self, prev_match_id=None):
		self.player1 = None
		self.player2 = None
		if prev_match_id is None:
			self.room_id = str(uuid.uuid4())
		else:
			self.room_id = str(prev_match_id)

	def __repr__(self):
		return f"MatchRoom(room_id={self.room_id}, player1={self.player1}, player2={self.player2})"

def create_room():
	room = MatchRoom()
	rooms.append(room)
	return room

def create_rematch_room(prev_match_id):
	room = MatchRoom(prev_match_id=prev_match_id)
	rematch_rooms.append(room)
	return room

def add_player_to_room(room: MatchRoom, player_id, channel_name):
	if room.player1 is None:
		room.player1 = Player(player_id, channel_name)
	elif room.player2 is None:
		room.player2 = Player(player_id, channel_name)

def find_room_to_join():
	for room in rooms:
		if room.player1 is None or room.player2 is None:
			pprint(f'Found match room: {room}')
			return room
	return None

def find_rematch_room_to_join(prev_match_id):
	for room in rematch_rooms:
		if room.room_id == str(prev_match_id):
			return room
	return None

def is_player_in_room_already(player_id) -> bool:
	for room in rooms + rematch_rooms:
		if room.player1 and player_id == room.player1.id:
			return True
		elif room.player2 and player_id == room.player2.id:
			return True
	return False

def get_player_state(player_id):
	try:
		user = CustomUser.objects.get(id=player_id)
		return user.state
	except CustomUser.DoesNotExist:
		return None

def get_prev_match(prev_match_id):
	try:
		prev_match = Match.objects.get(id=prev_match_id)
		return prev_match
	except Match.DoesNotExist:
		return None

def set_rematch_data(prev_match):
	try:
		data = {
				'player1' : prev_match.player2.id,
				'player2' : prev_match.player1.id,
				'default_ball_size' : GAME_CONSTANTS['BALL_SIZE'],
				'default_paddle_height' : GAME_CONSTANTS['PADDLE_HEIGHT'],
				'default_paddle_width' : GAME_CONSTANTS['PADDLE_WIDTH'],
				'default_paddle_speed' : GAME_CONSTANTS['PADDLE_SPEED']
			}
		return data
	except Match.DoesNotExist:
		return None
	
def set_user_to_ingame(player_id):
	user = CustomUser.objects.get(id=player_id)
	user.state = CustomUser.StateOptions.INGAME
	user.save(update_fields=["state"])

class MatchmakingConsumer(WebsocketConsumer):
	def connect(self):
		self.id = self.scope['user'].id
		print(f"Player {self.id} wants to play a match!")
		if is_player_in_room_already(self.id) or get_player_state(self.id) == CustomUser.StateOptions.INGAME:
			self.close()
			return
		room = find_room_to_join()
		if not room:
			room = create_room()
		add_player_to_room(room, self.id, self.channel_name)
		self.room_group_name = room.room_id
		async_to_sync(self.channel_layer.group_add)(
			self.room_group_name, self.channel_name
		)
		self.accept()
		if all([room.player1, room.player2]):
			data = {
				'player1' : room.player1.id,
				'player2' : room.player2.id,
				'default_ball_size' : GAME_CONSTANTS['BALL_SIZE'],
				'default_paddle_height' : GAME_CONSTANTS['PADDLE_HEIGHT'],
				'default_paddle_width' : GAME_CONSTANTS['PADDLE_WIDTH'],
				'default_paddle_speed' : GAME_CONSTANTS['PADDLE_SPEED']
			}
			match_serializer = MatchSerializer(data=data)
			if match_serializer.is_valid():
				match_serializer.save()
				#set_user_to_ingame(list(room['players'][0].keys())[0])
				#set_user_to_ingame(list(room['players'][1].keys())[0])
				async_to_sync(self.channel_layer.group_send)(
					self.room_group_name, {"type": "matchmaking_message", "message": match_serializer.data['id']}
				)
				print("Rooms after connect:")
				pprint(rooms)
		print("Rooms after connect:")
		pprint(rooms)

	def disconnect(self, close_code):
		for room in rooms:
			if (room.player1 is not None and room.player1.channel_name == self.channel_name) or (room.player2 is not None and room.player2.channel_name == self.channel_name):
				self.channel_layer.group_discard(self.room_group_name, self.channel_name)
				if (room.player1 is not None) and (self.id == room.player1.id):
					room.player1 = None
				else:
					room.player2 = None
				if (room.player1 is None) and (room.player2 is None):
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
		self.close() # closes the websocket once the match_id has been sent to both of the players


# implement 10 sec or so timeout
# protect against joining a rematch when it's not yours to join
# protect against being able to join when already waiting
class RematchConsumer(WebsocketConsumer):
	def connect(self):
		self.id = self.scope['user'].id
		prev_match_id = self.scope['url_route']['kwargs'].get('prev_match_id')
		prev_match = get_prev_match(prev_match_id)
		print(f"Player {self.id} wants a rematch!")
		if (is_player_in_room_already(self.id) or get_player_state(self.id) == CustomUser.StateOptions.INGAME
	  		or prev_match is None):
			self.close()
			return
		room = find_rematch_room_to_join(prev_match_id)
		if not room:
			room = create_rematch_room(prev_match_id)
		add_player_to_room(room, self.id, self.channel_name)
		self.room_group_name = room.room_id
		async_to_sync(self.channel_layer.group_add)(
			self.room_group_name, self.channel_name
		)
		self.accept()
		if all([room.player1, room.player2]):
			data = set_rematch_data(prev_match)
			match_serializer = MatchSerializer(data=data)
			if match_serializer.is_valid():
				match_serializer.save()
				#set_user_to_ingame(list(room['players'][0].keys())[0])
				#set_user_to_ingame(list(room['players'][1].keys())[0])
				async_to_sync(self.channel_layer.group_send)(
					self.room_group_name, {"type": "matchmaking_message", "message": match_serializer.data['id']}
				)
				print("Rematch rooms after connect:")
				pprint(rematch_rooms)
		print("Rematch rooms after connect:")
		pprint(rematch_rooms)

	def disconnect(self, close_code):
		for room in rematch_rooms:
			if (room.player1 is not None and room.player1.channel_name == self.channel_name) or (room.player2 is not None and room.player2.channel_name == self.channel_name):
				self.channel_layer.group_discard(self.room_group_name, self.channel_name)
				if (room.player1 is not None) and (self.id == room.player1.id):
					room.player1 = None
				else:
					room.player2 = None
				if (room.player1 is None) and (room.player2 is None):
					rematch_rooms.remove(room)
				break
		print("Rematch rooms after disconnect:")
		pprint(rematch_rooms)
	
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
		self.close() # closes the websocket once the match_id has been sent to both of the players