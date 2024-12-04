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
		self.capacity = 4

	def __repr__(self):
		return f"TournamentRoom(id={self.id}, players={self.players}, brackets={self.brackets}, capacity={self.capacity})"
class Player:
	def __init__(self, player_id, channel_name, tournament_username):
		self.id = player_id
		self.channel_name = channel_name
		self.username = tournament_username

	def __repr__(self):
		return f"Player(id={self.id}, channel_name={self.channel_name}, username={self.username})"
class Match:
	
	def __init__(self, id, round, player1, player2):
		self.id = id
		self.round = round
		self.players = [player1, player2]
		self.winner = None

	def __repr__(self):
		return f"Match(id={self.id}, round={self.round}, players={self.players})"

def is_player_in_tournament_room_already(player_id):
	for tournament_room in tournament_rooms:
		for player in tournament_room.players:
			if player is not None and player_id == player.id:
				return True
	return False

def get_tournament_room(tournament_id):
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

def get_match(tournament, match_id):
	for match in tournament.brackets:
		if match.id == match_id:
			return match
	return None

def get_match_index_in_brackets(tournament, match_id):
	i = 0
	for match in tournament.brackets:
		if (match.id == match_id):
			break
		i += 1
	return i

def get_match_by_round(tournament_room, round):
	for match in tournament_room.brackets:
		if match.round == round:
			return match
	return None

def get_player_from_tournament_room(tournament_room, player_id):
	for player in tournament_room.players:
		if player.id == player_id:
			return player
	return None

class TournamentConsumer(WebsocketConsumer):
	def connect(self):
		self.id = self.scope['user'].id
		capacity = 4 # CHANGE to tournament capacity
		tournament_id = int(self.scope['url_route']['kwargs'].get('tournament_id'))
		print(f"Player {self.id} wants to play tournament {tournament_id} with capacity {capacity}!")
		# Check for valid player_id and tournament_id pair
		try:
			tournament = Tournament.objects.get(id=tournament_id)
		except ObjectDoesNotExist:
			print("Close bcs no such tournament")
			self.close()
			return
		try:
			player_tournament = PlayerTournament.objects.get(player=self.id, tournament=tournament_id)
		except ObjectDoesNotExist:
			print("Reject bcs invalid player_tournament pair.")
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
		tournament_room = get_tournament_room(tournament_id)
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
		# Round 1 and round 2
		if len(tournament_room.players) == capacity:
			self.create_match_and_return_match_id(tournament_room, 1, tournament_room.players[0], tournament_room.players[1])
			self.create_match_and_return_match_id(tournament_room, 2, tournament_room.players[2], tournament_room.players[3])
		#	self.create_match_and_return_match_id(tournament_room, 3, tournament_room.players[4], tournament_room.players[5])
		#	self.create_match_and_return_match_id(tournament_room, 4, tournament_room.players[6], tournament_room.players[7])
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

	def create_match_and_return_match_id(self, tournament_room, round, player1, player2):
		# DATABASE update
		# Create group_names for each round
		round_group_name = "round" + str(round) + str(tournament_room.id)
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
			# TOURNAMENT_ROOM update
			match = Match(match_serializer1.data['id'], round, player1, player2)
			tournament_room.brackets.append(match)
			async_to_sync(self.channel_layer.group_send)(
				round_group_name, {"type": "tournament_message", "message": match_serializer1.data['id']}
			)

	def receive(self, text_data):
		text_data_json = json.loads(text_data)
		message_type = text_data_json["message"]
		print(f"Message in receive: {message_type}")

		if message_type == "match_end":
			match_id = int(text_data_json["match_id"])
			winner_id = int(text_data_json["winner_id"])
			self.next_round(match_id, winner_id)

	#	# Send message to room group
	#	async_to_sync(self.channel_layer.group_send)(
	#		self.room_group_name, {"type": "tournament_message", "message": message_type}
	#	)

	def create_match_and_return_match_id_next_round(self, tournament_room, round):
		match = get_match_by_round(tournament_room, round)
		if match is None:
			print("Match not found in tournament room, creating...")
			player1 = get_player_from_tournament_room(tournament_room, self.id)
			print(f"Player1: {player1.id}")
			match = Match(None, round, player1, None)
			tournament_room.brackets.append(match)
		else:
			print("Match found in tournament room, adding player...")
			player2 = get_player_from_tournament_room(tournament_room, self.id)
			print(f"Player2: {player2.id}")
			match.players[1] = player2
		print(f"Next round match: {match}")
		player1 = match.players[0]
		player2 = match.players[1]
		if (player1 is not None and player2 is not None):
			print(f"Creating match for round: {match.round}")
			# DATABASE update
			# Create group_names for each round
			round_group_name = "round" + str(round) + str(tournament_room.id)
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
				match.id = match_serializer1.data['id'] # NoneType winner error
				async_to_sync(self.channel_layer.group_send)(
					round_group_name, {"type": "tournament_message", "message": match_serializer1.data['id']}
			)
		print("End of next_round")



	def next_round(self, match_id, winner_id):
		print("Next round function")
		tournament_id = int(self.scope['url_route']['kwargs'].get('tournament_id'))
		tournament_room = get_tournament_room(tournament_id)
		print(f"Next round function, tournament: {tournament_room}")
		match = get_match(tournament_room, match_id)
		# Update match in brackets
		match.winner = winner_id
	#	if (match.round <= tournament_room.capacity / 2):
			# round_number = 1
			# j = 1
			# k = 1
			# while (round_number <= tournament_room.capacity / 2 - 1):
			# 	if match.round in (j, j+1):
			# 		self.add_player_to_match_in_tournament_room(tournament_room, tournament_room.capacity / 2 + k)
			# 		round_number += 1

		print(f"Next round function, match.round: {match.round}")
		if match.round == tournament_room.capacity - 1:
			round_group_name = "round" + str(match.round) + str(tournament_room.id)
			async_to_sync(self.channel_layer.group_send)(
				round_group_name, {"type": "tournament_message", "message": "tournament_end"}
			)
			#do stuff
		if (match.round in (1, 2)):
			self.create_match_and_return_match_id_next_round(tournament_room, tournament_room.capacity / 2 + 1)
		elif (match.round in (3, 4)):
			self.create_match_and_return_match_id_next_round(tournament_room, tournament_room.capacity / 2 + 2)
		elif (match.round in (5, 6)):
			self.create_match_and_return_match_id_next_round(tournament_room, tournament_room.capacity / 2 + 3)
	#	elif (match.round in (7, 8)):
	#		self.add_player_to_match_in_tournament_room(tournament_room, tournament_room.capacity / 2 + 4)
	#	elif (match.round in (9, 10)):
	#		self.add_player_to_match_in_tournament_room(tournament_room, tournament_room.capacity / 2 + 5)
	#	elif (match.round in (11, 12)):
	#		self.add_player_to_match_in_tournament_room(tournament_room, tournament_room.capacity / 2 + 6)
	#	elif (match.round in (13, 14)):
	#		self.add_player_to_match_in_tournament_room(tournament_room, tournament_room.capacity / 2 + 7)
		#elif (match.round <= ):
				
			
	
	def tournament_message(self, event):
		message = event["message"]
		print(f"Received group message: {message}")
		self.send(text_data=json.dumps({"message": message}))
		#self.close() # closes the websocket once the match_id has been sent to both of the players