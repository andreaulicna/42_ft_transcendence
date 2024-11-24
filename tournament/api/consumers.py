from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import uuid # unique room_id
from pprint import pprint # nice printing
from .models import CustomUser, Match, PlayerTournament, Tournament
import json
from .serializers import MatchSerializer
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist

tournament_rooms = []

class TournamentRoom:
	def __init__(self, tournament_id):
		self.id = tournament_id
		self.players = []

	def __repr__(self):
		return f"TournamentRoom(id={self.id}, players={self.players})"

class Player:
	def __init__(self, player_id, channel_name, tournament_username):
		self.id = player_id
		self.channel_name = channel_name
		self.username = tournament_username

	def __repr__(self):
		return f"Player(id={self.id}, channel_name={self.channel_name}, username={self.username})"

def is_player_in_tournament_room_already(player_id):
	for tournament_room in tournament_rooms:
		for player in tournament_room.players:
			if player is not None and player_id == player.id:
				return True
	return False

def find_tournament_room_to_join(tournament_id):
	for tournament_room in tournament_rooms:
		if (tournament_room.id == tournament_id) and (len(tournament_room.players) < 4): # CHANGE to tournament capacity
			pprint(f'Found tournament room: {tournament_room}')
			return tournament_room
	return None

def find_player_in_tournament_room(player_id):
	for tournament_room in tournament_rooms:
		if player_id in tournament_room.players:
			return tournament_room
	return None

def get_player_state(player_id):
	try:
		user = CustomUser.objects.get(id=player_id)
		return user.state
	except CustomUser.DoesNotExist:
		return None

def create_tournament_room(tournament_id):
	tournament_database = get_object_or_404(Tournament, id=tournament_id)
	tournament_room = TournamentRoom(tournament_id)
	tournament_rooms.append(tournament_room)
	return tournament_room

def add_player_to_tournament_room(tournament_room, player_id, channel_name, player_tournament_tmp_username):
	if (player_tournament_tmp_username):
		tournament_username = player_tournament_tmp_username
	else:
		player = CustomUser.objects.filter(id=player_id)
		tournament_username = player.username
	tournament_room.players.append(Player(player_id, channel_name, tournament_username))


class TournamentConsumer(WebsocketConsumer):
	def connect(self):
		self.id = self.scope['user'].id
		capacity = 4 # CHANGE to tournament capacity
		tournament_id = int(self.scope['url_route']['kwargs'].get('tournament_id'))
		print(f"Player {self.id} wants to play tournament {tournament_id} with capacity {capacity}!")
		# Check for valid player_id and tournament_id pair
		try:
			player_tournament = PlayerTournament.objects.get(player=self.id, tournament=tournament_id)
		except ObjectDoesNotExist:
			print("Reject bcs invalid player_tournament pair.")
			self.close()
			return
		if is_player_in_tournament_room_already(self.id) or get_player_state(self.id) == CustomUser.StateOptions.INGAME:
			print("Reject bcs already in a tournament")
			self.close()
			return 
		print(f"Finding room")
		tournament_room = find_tournament_room_to_join(tournament_id)
		if not tournament_room:
			try:
				tournament_room = create_tournament_room(tournament_id)
				print(f"Room {tournament_room.id} created!")
			except Http404:
				print("Close bcs no such tournament")
				self.close()
				return
		add_player_to_tournament_room(tournament_room, self.id, self.channel_name, player_tournament.player_tmp_username)
		self.room_group_name = str(tournament_room.id)
		async_to_sync(self.channel_layer.group_add)(
			self.room_group_name, self.channel_name
		)
		self.accept()
		if len(tournament_room.players) == 4: # CHANGE to tournamet capacity
			# Create group_names for each round
			round1_group_name = "round1_" + str(tournament_room.id)
			round2_group_name = "round2_" + str(tournament_room.id)
			# Assign players to group_names for each round
			async_to_sync(self.channel_layer.group_add)(
				round1_group_name, tournament_room.players[0].channel_name
			)
			async_to_sync(self.channel_layer.group_add)(
				round1_group_name, tournament_room.players[1].channel_name
			)
			async_to_sync(self.channel_layer.group_add)(
				round2_group_name, tournament_room.players[2].channel_name
			)
			async_to_sync(self.channel_layer.group_add)(
				round2_group_name, tournament_room.players[3].channel_name
			)
			# Create math for round 1 and return match_id to players
			data1 = {
				'player1' : tournament_room.players[0].id,
				'player2' : tournament_room.players[1].id,
				'tournament' : tournament_room.id,
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
				'player1' : tournament_room.players[2].id,
				'player2' : tournament_room.players[3].id,
				'tournament' : tournament_room.id,
				'round' : 2
			}
			match_serializer2 = MatchSerializer(data=data2)
			if match_serializer2.is_valid():
				match_serializer2.save()
				async_to_sync(self.channel_layer.group_send)(
					round2_group_name, {"type": "tournament_message", "message": match_serializer2.data['id']}
				)
		print("Tournaments after connect:")
		pprint(tournament_rooms)

	def disconnect(self, close_code):
		for tournament_room in tournament_rooms:
			for player in tournament_room.players:
				if self.channel_name == player.channel_name:
					async_to_sync(self.channel_layer.group_discard)(
						self.room_group_name, self.channel_name
					)
					tournament_room.players.remove(player)
					if not tournament_room.players:
						tournament_rooms.remove(tournament_room)
					break
		print("Tournaments after disconnect:")
		pprint(tournament_rooms)
	
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