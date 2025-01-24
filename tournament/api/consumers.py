from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import uuid # unique room_id
from pprint import pprint # nice printing
from .models import CustomUser, Match, PlayerTournament, Tournament, LocalTournament, LocalMatch
import json
from .serializers import MatchSerializer, LocalMatchSerializer
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy
from django.db import models
import logging
from tournament.settings import GAME_CONSTANTS

tournament_rooms = []
local_tournament_rooms = []

class AbstractTournamentRoom:
	def __init__(self, tournament_id, capacity, creator_id):
		self.id = tournament_id
		self.players = []
		self.brackets = []
		self.capacity = capacity
		self.creator_id = creator_id

	def __repr__(self):
		return f"{self.__class__.__name__}(id={self.id}, players={self.players}, brackets={self.brackets}, capacity={self.capacity})"

	def brackets_to_json(self):
		return {
			"capacity": self.capacity,
			"brackets": [match.brackets_to_json() for match in self.brackets],
		}

class TournamentRoom(AbstractTournamentRoom):
	def __init__(self, tournament_id, capacity, creator_id):
		super().__init__(tournament_id, capacity, creator_id)
		self.tournament_group_name = str(tournament_id) + "_tournament"

class LocalTournamentRoom(AbstractTournamentRoom):
	def __init__(self, tournament_id, capacity, creator_id):
		super().__init__(tournament_id, capacity, creator_id)
		self.current_brackets_stage = 0

	def __repr__(self):
		return f"{self.__class__.__name__}(id={self.id}, creator_id={self.creator_id}, players={self.players}, brackets={self.brackets}, capacity={self.capacity})"

class AbstractPlayer:
	def __init__(self, username):
		self.username = username

	def __repr__(self):
		return f"{self.__class__.__name__}(username={self.username})"

class Player(AbstractPlayer):
	def __init__(self, player_id, channel_name, username):
		super().__init__(username)
		self.id = player_id
		self.channel_name = channel_name

	def __repr__(self):
		return f"{self.__class__.__name__}(id={self.id}, username={self.username}, channel_name={self.channel_name})"

class LocalPlayer(AbstractPlayer):
	def __init__(self, username):
		super().__init__(username)

class Match:
	def __init__(self, id, round, player1, player2, tournament_group_name):
		self.id = id
		self.round = round
		self.players = [player1, player2]
		self.winner = None
		self.round_group_name = tournament_group_name + "_round_" + str(round) # not used for local tournament
		self.brackets_stage = 0

	def brackets_to_json(self):
		return {
			"round": self.round,
			"player1_username": self.players[0].username if self.players[0] else None,
			"player2_username": self.players[1].username if self.players[1] else None,
		}

	def __repr__(self):
		return f"Match(id={self.id}, round={self.round}, players={self.players}, round_group_name={self.round_group_name})"

def is_player_in_local_or_remote_tournament_room_already(player_id):
	for tournament_room in tournament_rooms:
		for player in tournament_room.players:
			if player is not None and player_id == player.id:
				return True
	for local_tournament_room in local_tournament_rooms:
		if local_tournament_room.creator_id == player_id:
			return True
	return False

def get_remote_or_local_tournament_room(rooms_to_parse, tournament_id):
	for room in rooms_to_parse:
		if (room.id == tournament_id):
			return room
	return None

#def find_player_in_tournament_room(player_id):
#	for tournament_room in tournament_rooms:
#		if player_id in tournament_room.players:
#			return tournament_room
#	return None

def get_player_state(player_id):
	user = get_object_or_404(CustomUser,id=player_id)
	return user.state

def create_tournament_room(tournament_id, capacity, creator_id):
	tournament_room = TournamentRoom(tournament_id, capacity, creator_id)
	tournament_rooms.append(tournament_room)
	return tournament_room

def create_local_tournament_room(tournament_id, capacity, creator_id, players):
	local_tournament_room = LocalTournamentRoom(tournament_id, capacity, creator_id)
	local_tournament_rooms.append(local_tournament_room)
	for player in players:
		local_tournament_room.players.append(LocalPlayer(player))
	return local_tournament_room


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
		tournament_id = int(self.scope['url_route']['kwargs'].get('tournament_id'))
		logging.info(f"Player {self.id} wants to play tournament {tournament_id}!")
		# Check if tournament exists
		try:
			tournament_database = Tournament.objects.get(id=tournament_id)
		except ObjectDoesNotExist:
			logging.info("Close bcs no such tournament")
			self.close()
			return
		logging.info(f"Tournament capacity is: {tournament_database.capacity}")
		# Check for valid player_id and tournament_id pair
		try:
			player_tournament = PlayerTournament.objects.get(player=self.id, tournament=tournament_id)
		except ObjectDoesNotExist:
			logging.info("Reject bcs invalid player_tournament pair.")
			self.close()
			return
		# Check for tournament state = FINISHED
		if tournament_database.status == Tournament.StatusOptions.FINISHED:
			logging.info("Reject bscs tournament finished")
			self.close()
			return
		# Check if player already in room to limit to one tournament ws
		if is_player_in_local_or_remote_tournament_room_already(self.id) is True:
			logging.info(f"Reject to limit to one tournament ws")
			self.close()
			return
		# Check for player being = INGAME
		if get_player_state(self.id) == CustomUser.StateOptions.INGAME:
			logging.info("Reject bcs already in a pong game")
			self.close()
			return
		# Add player to room or create it
		tournament_room = get_remote_or_local_tournament_room(tournament_rooms, tournament_id)
		logging.info(f'Found tournament room: {tournament_room}')
		if not tournament_room:
			tournament_room = create_tournament_room(tournament_id, tournament_database.capacity, tournament_database.creator.id)
			logging.info(f"Room {tournament_room.id} created!")
		add_player_to_tournament_room(tournament_room, self.id, self.channel_name, player_tournament.player_tmp_username)
		async_to_sync(self.channel_layer.group_add)(
			tournament_room.tournament_group_name, self.channel_name
		)
		self.accept()
		self.send_lobby_update_message(tournament_room.tournament_group_name, "player_join", self.scope['user'])
		# First set of rounds
		if len(tournament_room.players) == tournament_room.capacity:
			round = 1
			player_iterator = 0
			while (round <= tournament_room.capacity / 2):
				self.create_match_and_return_match_id(tournament_room, round, tournament_room.players[player_iterator], tournament_room.players[player_iterator + 1])
				round += 1
				player_iterator += 2

		logging.info("Tournaments after connect:")
		logging.info(tournament_rooms)

	def disconnect(self, close_code):
		logging.info(f"Disconnecting player {self.id} from tournament")
		for tournament_room in tournament_rooms:
			for player in tournament_room.players:
				if self.channel_name == player.channel_name:
					async_to_sync(self.channel_layer.group_discard)(
						tournament_room.tournament_group_name, self.channel_name
					)
					if (self.id == tournament_room.creator_id):
						self.send_lobby_update_message(tournament_room.tournament_group_name, "creator_cancel", self.scope['user'])
					else:
						self.send_lobby_update_message(tournament_room.tournament_group_name, "player_cancel", self.scope['user'])
					tournament_room.players.remove(player)
					if not tournament_room.players:
						tournament_rooms.remove(tournament_room)
					break
		logging.info("Tournaments after disconnect:")
		logging.info(tournament_rooms)

	def create_match_and_return_match_id(self, tournament_room, round, player1, player2):
		# Create group_names for each round
		round_group_name = tournament_room.tournament_group_name + "_" + str(round) + "_round"
		# Assign players to group_names for each round
		async_to_sync(self.channel_layer.group_add)(
			round_group_name, player1.channel_name
		)
		async_to_sync(self.channel_layer.group_add)(
			round_group_name, player2.channel_name
		)
		# Create match for round and return match_id to players
		# DATABASE update
		match_data = {
			'player1' : player1.id,
			'player2' : player2.id,
			'tournament' : tournament_room.id,
			'round_number' : round,
			'default_ball_size' : GAME_CONSTANTS['BALL_SIZE'],
			'default_paddle_height' : GAME_CONSTANTS['PADDLE_HEIGHT'],
			'default_paddle_width' : GAME_CONSTANTS['PADDLE_WIDTH'],
			'default_paddle_speed' : GAME_CONSTANTS['PADDLE_SPEED']
		}
		match_serializer = MatchSerializer(data=match_data)
		if match_serializer.is_valid():
			match_serializer.save()
			# TOURNAMENT_ROOM update
			match = Match(match_serializer.data['id'], round, player1, player2, tournament_room.tournament_group_name)
			tournament_room.brackets.append(match)
			async_to_sync(self.channel_layer.group_send)(
				round_group_name, {"type": "tournament_message", "message": match_serializer.data['id']}
			)
		else:
			# Log the errors
			logging.error(f"Match serializer errors: {match_serializer.errors}")
			# Send error message to the room
			async_to_sync(self.channel_layer.group_send)(
				round_group_name, {"type": "tournament_message", "message": {"error": match_serializer.errors}}
			)

	def receive(self, text_data):
		text_data_json = json.loads(text_data)
		message_type = text_data_json["message"]
		logging.info(f"Message in receive: {message_type}")

		if message_type == "match_end":
			match_id = int(text_data_json["match_id"])
			winner_id = int(text_data_json["winner_id"])
			if (self.id == winner_id):
				self.next_round(match_id, winner_id)

	def create_match_and_return_match_id_next_round(self, tournament_room, round):
		match = get_match_by_round(tournament_room, round)
		if match is None:
			logging.info("Match not found in tournament room, creating...")
			player1 = get_player_from_tournament_room(tournament_room, self.id)
			logging.info(f"Player1: {player1.id}")
			match = Match(None, round, player1, None, tournament_room.tournament_group_name)
			tournament_room.brackets.append(match)
		else:
			logging.info("Match found in tournament room, adding player...")
			player2 = get_player_from_tournament_room(tournament_room, self.id)
			logging.info(f"Player2: {player2.id}")
			match.players[1] = player2
		logging.info(f"Next round match: {match}")
		player1 = match.players[0]
		player2 = match.players[1]
		if (player1 is not None and player2 is not None):
			logging.info(f"Creating match for round: {match.round}")
			# Assign players to group_names for each round
			async_to_sync(self.channel_layer.group_add)(
				match.round_group_name, player1.channel_name
			)
			async_to_sync(self.channel_layer.group_add)(
				match.round_group_name, player2.channel_name
			)
			# Create math for round and return match_id to players
			# DATABASE update
			match_data = {
				'player1' : player1.id,
				'player2' : player2.id,
				'tournament' : tournament_room.id,
				'round_number' : round,
				'default_ball_size' : GAME_CONSTANTS['BALL_SIZE'],
				'default_paddle_height' : GAME_CONSTANTS['PADDLE_HEIGHT'],
				'default_paddle_width' : GAME_CONSTANTS['PADDLE_WIDTH'],
				'default_paddle_speed' : GAME_CONSTANTS['PADDLE_SPEED']
			}
			match_serializer = MatchSerializer(data=match_data)
			if match_serializer.is_valid():
				match_serializer.save()
				match.id = match_serializer.data['id'] # NoneType winner error
				logging.info(f"Group name for match {match.id}: {match.round_group_name}")
				async_to_sync(self.channel_layer.group_send)(
					match.round_group_name, {"type": "tournament_message", "message": match_serializer.data['id']}
			)
		logging.info("End of next_round")

	def next_round(self, match_id, winner_id):
		tournament_id = int(self.scope['url_route']['kwargs'].get('tournament_id'))
		tournament_room = get_remote_or_local_tournament_room(tournament_rooms, tournament_id)
		match = get_match(tournament_room, match_id)
		# Update match in brackets
		match.winner = winner_id

		if match.round == tournament_room.capacity - 1:
			async_to_sync(self.channel_layer.group_send)(
				match.round_group_name, {"type": "tournament_message", "message": "tournament_end"}
			)
			logging.info(f"Message sent to group: {match.round_group_name}")
			try:
				tournament_database = Tournament.objects.get(id=tournament_id)
				tournament_database.status = Tournament.StatusOptions.FINISHED
				tournament_database.save()
			except ObjectDoesNotExist:
				logging.info("Close bcs no such tournament")
				self.close()
				return

		increment = 1
		current_round = 1
		while(match.round < tournament_room.capacity - 1):
			if (match.round in (current_round, current_round + 1)):
				self.create_match_and_return_match_id_next_round(tournament_room, int(tournament_room.capacity / 2) + increment)
				break
			increment += 1
			current_round += 2

	def tournament_message(self, event):
		message = event["message"]
		logging.info(f"Received group message: {message}")
		self.send(text_data=json.dumps({"message": message}))
		#self.close() # closes the websocket once the match_id has been sent to both of the players

	def send_lobby_update_message(self, tournament_group_name, message, user):
		async_to_sync(self.channel_layer.group_send)(
			tournament_group_name, {
				"type": "remote_tournament_lobby_update", 
				"message": message,
				"player_id": self.id,
				"player_username": user.username, 
			}
		)
	
	def remote_tournament_lobby_update(self, event):
		message = event['message']
		player_id = event['player_id']
		player_username = event['player_username']

		if player_id != self.id:
			self.send(text_data=json.dumps({
				'type': 'remote_tournament_lobby_update',
				'message': message,
				'player_id': player_id,
				'player_username': player_username
			}))


class LocalTournamentConsumer(WebsocketConsumer):
	def connect(self):
		self.id = self.scope['user'].id
		local_tournament_id = int(self.scope['url_route']['kwargs'].get('local_tournament_id'))
		logging.info(f"Player {self.id} wants to play tournament {local_tournament_id}!")
		# Check if tournament exists
		try:
			local_tournament_database = LocalTournament.objects.get(id=local_tournament_id)
		except ObjectDoesNotExist:
			logging.info("Close bcs no such local tournament")
			self.close()
			return
		logging.info(f"Local tournament capacity is: {local_tournament_database.capacity}")
		# Check for valid creator for the given tournament
		if (local_tournament_database.creator.id != self.id):
			logging.info("Close bcs invalid creator")
			self.close()
			return
		# Check for tournament state = FINISHED
		if local_tournament_database.status == LocalTournament.StatusOptions.FINISHED:
			logging.info("Reject bscs tournament finished")
			self.close()
			return
		# Check if player already in room to limit to one tournament ws
		if is_player_in_local_or_remote_tournament_room_already(self.id) is True:
			logging.info(f"Reject to limit to one tournament ws")
			self.close()
			return
		# Check for player being = INGAME
		if get_player_state(self.id) == CustomUser.StateOptions.INGAME:
			logging.info("Reject bcs already in a pong game")
			self.close()
			return
		local_tournament_room = create_local_tournament_room(local_tournament_id, local_tournament_database.capacity, self.id, local_tournament_database.players)
		logging.info(f'Local tournament room: {local_tournament_room}')
		self.accept()
		# First set of rounds
		local_tournament_room.current_brackets_stage = 1
		if len(local_tournament_room.players) == local_tournament_room.capacity:
			round = 1
			player_iterator = 0
			while (round <= local_tournament_room.capacity / 2):
				self.create_local_match_for_round(local_tournament_room, round, local_tournament_room.players[player_iterator], local_tournament_room.players[player_iterator + 1])
				round += 1
				player_iterator += 2
		self.play_match_or_create_more_brackets(local_tournament_room)

		logging.info("Local tournaments after connect:")
		logging.info(local_tournament_rooms)

	def disconnect(self, close_code):
		logging.info(f"Disconnecting player {self.id} from local tournament")
		for local_tournament_room in local_tournament_rooms:
			if local_tournament_room.creator_id == self.id:
				local_tournament_rooms.remove(local_tournament_room)
				break
		logging.info("Tournaments after disconnect:")
		logging.info(tournament_rooms)

	
	def create_local_match_for_round(self, local_tournament_room, round, player1, player2):
		# Create math for round and return match_id to players
		# DATABASE update
		logging.info(f"Round: {round}, tournament: {local_tournament_room.id}")
		player2_tmp_username = player2.username if player2 else ""
		local_match_data = {
			'tournament': local_tournament_room.id,
			'round_number': round,
			'creator': local_tournament_room.creator_id,
			'player1_tmp_username': player1.username,
			'player2_tmp_username': player2_tmp_username,
			'default_ball_size': GAME_CONSTANTS['BALL_SIZE'],
			'default_paddle_height': GAME_CONSTANTS['PADDLE_HEIGHT'],
			'default_paddle_width': GAME_CONSTANTS['PADDLE_WIDTH'],
			'default_paddle_speed': GAME_CONSTANTS['PADDLE_SPEED']
		}
		logging.info(f"Local match data: {local_match_data}")
		local_match_serializer = LocalMatchSerializer(data=local_match_data)
		if local_match_serializer.is_valid():
			local_match_serializer.save()
			# TOURNAMENT_ROOM update
			local_match = Match(local_match_serializer.data['id'], round, player1, player2, "local")
			local_match.brackets_stage = local_tournament_room.current_brackets_stage
			local_tournament_room.brackets.append(local_match)
		else:
			# Log the errors
			logging.error(f"LocalMatch serializer errors: {local_match_serializer.errors}")

	def	play_match_or_create_more_brackets(self, local_tournament_room):
		last_match = local_tournament_room.brackets[-1] if local_tournament_room.brackets else None
		# End of tournament
		if (len(local_tournament_room.brackets) == local_tournament_room.capacity - 1) and (last_match.winner is not None):
			self.send(text_data=json.dumps({
				"type": "local_tournament_message", 
				"message": "tournament_end"
			}))
			return 
		# Play match in current bracket round
		for match in local_tournament_room.brackets:
			if (match.brackets_stage == local_tournament_room.current_brackets_stage and match.winner is None):
				self.send(text_data=json.dumps({
					"type": "local_tournament_message", 
					"message": match.id
				}))
				return
		# Play the first match in the current bracket round
		local_tournament_room.current_brackets_stage += 1
		for match in local_tournament_room.brackets:
			if match.brackets_stage == local_tournament_room.current_brackets_stage:
				self.send(text_data=json.dumps({
					"type": "local_tournament_message", 
					"message": match.id
				}))
				return

	def receive(self, text_data):
		text_data_json = json.loads(text_data)
		message_type = text_data_json["message"]
		logging.info(f"Message in receive: {message_type}")
		local_tournament_id = int(self.scope['url_route']['kwargs'].get('local_tournament_id'))
		local_tournament_room = get_remote_or_local_tournament_room(local_tournament_rooms, local_tournament_id)

		if message_type == "match_end":
			match_id = int(text_data_json["match_id"])
			winner_username = text_data_json["winner_username"]
			self.update_winner_in_match(local_tournament_id, match_id, winner_username)
			current_match = get_match(local_tournament_room, match_id)
			last_match = local_tournament_room.brackets[-1] if local_tournament_room.brackets else None
			if (len(local_tournament_room.brackets) != local_tournament_room.capacity - 1) or (last_match.winner is None):
				if (last_match.players[1] is None):
					logging.info("Adding player 1")
					last_match.players[1] = current_match.winner
					match_database = LocalMatch.objects.get(id=last_match.id)
					match_database.player2_tmp_username = last_match.players[1].username
					match_database.save()
				elif (last_match.players[0] is not None):
					logging.info("Adding new bracket and player 0")
					self.create_local_match_for_round(local_tournament_room, last_match.round + 1, current_match.winner, None)
			logging.info(local_tournament_room.brackets_to_json())
			self.send(text_data=json.dumps({
				"message": "brackets",
				**local_tournament_room.brackets_to_json(), # the ** operator unpacks the dictionary returned by brackets_to_json and include its contents in the JSON object being sent
			}))
		
		if message_type == "continue":
			self.play_match_or_create_more_brackets(local_tournament_room)
	
	def update_winner_in_match(self, local_tournament_id , match_id, winner_username):
		local_tournament_room = get_remote_or_local_tournament_room(local_tournament_rooms, local_tournament_id)
		for match in local_tournament_room.brackets:
			if (match.id == match_id):
				if (winner_username == match.players[0].username):
					match.winner = match.players[0]
				else:
					match.winner = match.players[1]
				break
