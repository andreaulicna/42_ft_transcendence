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
from django.utils.translation import gettext_lazy
from django.db import models

tournament_rooms = []
class TournamentRoom:
	def __init__(self, tournament_id):
		self.id = tournament_id
		self.players = []
		self.brackets = []

	def __repr__(self):
		return f"TournamentRoom(id={self.id}, players={self.players}, brackets={self.brackets})"
class Player:
	def __init__(self, player_id, channel_name, tournament_username):
		self.id = player_id
		self.channel_name = channel_name
		self.username = tournament_username
		self.is_ingame = False 

	def __repr__(self):
		return f"Player(id={self.id}, channel_name={self.channel_name}, username={self.username}, is_ingame={self.is_ingame})"
class Match:
	class StatusOptions(models.TextChoices):
		INPROGRESS = "IP", gettext_lazy("In progress")
		FINISHED = "FIN", gettext_lazy("Finished")
	
	def __init__(self, round, player1, player2, status=StatusOptions.INPROGRESS):
		self.round = round
		self.players = [player1, player2]
		self.status = status

	def __repr__(self):
		return f"Match(round={self.round}, players={self.players}, status={self.status})"

def is_player_in_tournament_room_already(player_id):
	for tournament_room in tournament_rooms:
		for player in tournament_room.players:
			if player is not None and player_id == player.id:
				return True
	return False

def find_tournament_room(tournament_id):
	for tournament_room in tournament_rooms:
		if (tournament_room.id == tournament_id):
			return tournament_room
	return None

#def find_player_in_tournament_room(player_id):
#	for tournament_room in tournament_rooms:
#		if player_id in tournament_room.players:
#			return tournament_room
#	return None

def get_player_state(player_id):
	try:
		user = CustomUser.objects.get(id=player_id)
		return user.state
	except CustomUser.DoesNotExist:
		return None

def get_tournament_status(tournament_id):
	try:
		tournament = Tournament.objects.get(id=tournament_id)
		return tournament.status
	except Tournament.DoesNotExist:
		return None

def create_tournament_room(tournament_id):
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

#def count_players_ingame(tournament_room):
#	count = 0
#	for player in tournament_room.players:
#		if player.is_ingame == True:
#			count += 1
#	return count

def create_match_and_return_match_id(self, tournament_room, round, player1, player2):
	# TOURNAMENT_ROOM update
	match = Match(round, player1, player2)
	tournament_room.brackets.append(match)
	player1.is_ingame = True
	player2.is_ingame = True
	# DATABASE update
	# Create group_names for each round
	round_group_name = "round" + str(round) + "_left_" + str(tournament_room.id)
	# Assign players to group_names for each round
	async_to_sync(self.channel_layer.group_add)(
		round_group_name, player1.channel_name
	)
	async_to_sync(self.channel_layer.group_add)(
		round_group_name, player2.channel_name
	)
	# Create math for round 1 and return match_id to players
	match_data = {
		'player1' : player1.id,
		'player2' : player2.id,
		'tournament' : tournament_room.id,
		'round' : round
	}
	match_serializer1 = MatchSerializer(data=match_data)
	if match_serializer1.is_valid():
		match_serializer1.save()
		async_to_sync(self.channel_layer.group_send)(
			round_group_name, {"type": "tournament_message", "message": match_serializer1.data['id']}
		)

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
		# Check that tournament exists
		if get_tournament_status(tournament_id) is None:
			print("Close bcs no such tournament")
			self.close()
			return
		# Check for tournament state = FINISHED
		if get_tournament_status(tournament_id) == Tournament.StatusOptions.FINISHED:
			print("Reject bcs tournament finished")
			self.close()
			return
		# Check if player already in room to limit to one tournament ws
		if is_player_in_tournament_room_already(self.id) is True:
			print(f"Reject to limit to one tournament ws")
			self.close()
			return
		# Check for player being = INGAME
		if get_player_state(self.id) == CustomUser.StateOptions.INGAME:
			print("Reject bcs already in a pong game")
			self.close()
			return
		# Add player to room or create it
		tournament_room = find_tournament_room(tournament_id)
		pprint(f'Found tournament room: {tournament_room}')
		if not tournament_room:
			tournament_room = create_tournament_room(tournament_id)
			print(f"Room {tournament_room.id} created!")
		add_player_to_tournament_room(tournament_room, self.id, self.channel_name, player_tournament.player_tmp_username)
		self.room_group_name = str(tournament_room.id)
		async_to_sync(self.channel_layer.group_add)(
			self.room_group_name, self.channel_name
		)
		self.accept()
		# Understand the tournament status
		# Round 1 match
		if len(tournament_room.players) >= 2 and len(tournament_room.brackets) == 0:
			create_match_and_return_match_id(self, tournament_room, 1, tournament_room.players[0], tournament_room.players[1])
		# Round 2 match
		if len(tournament_room.players) == 4 and len(tournament_room.brackets) in (0, 1):
			create_match_and_return_match_id(self, tournament_room, 2, tournament_room.players[2], tournament_room.players[3])
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
		#self.close() # closes the websocket once the match_id has been sent to both of the players