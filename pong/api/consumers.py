from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import CustomUser, Match
from pprint import pprint # nice printing
import json
from django.shortcuts import get_object_or_404
import random
from asgiref.sync import sync_to_async

match_rooms = []

from pprint import pprint

class PongGame:
	def __init__(self, match_id):
		self.match_id = match_id
		self.game_width = 160
		self.game_height = 100
		self.default_paddle_height = self.game_height / (10 * 2)  # adjusted for a half
		self.default_paddle_width = 2 / 2  # adjusted for a half
		self.paddle1 = Paddle(x=-80 + self.default_paddle_width, game=self)
		self.paddle2 = Paddle(x=80 - self.default_paddle_width, game=self)
		self.player1 = None
		self.player2 = None

	def __repr__(self):
		return (f"PongGame(match_id={self.match_id}, game_width={self.game_width}, "
				f"game_height={self.game_height}, paddle1={self.paddle1}, paddle2={self.paddle2}, "
				f"player1={self.player1}, player2={self.player2})")

class Paddle:
	def __init__(self, x, game):
		self.x = x
		self.y = 0
		self.paddle_height = game.default_paddle_height
		self.paddle_width = game.default_paddle_width

	def __repr__(self):
		return f"Paddle(x={self.x}, y={self.y}, paddle_height={self.paddle_height}, paddle_width={self.paddle_width})"

class Player:
	def __init__(self, player_id, channel_name):
		self.id = player_id
		self.channel_name = channel_name

	def __repr__(self):
		return f"Player(id={self.id}, channel_name={self.channel_name})"

def create_match_room(match_id):
	match_room = PongGame(match_id)
	match_rooms.append(match_room)
	return match_room

def is_player_in_match_room_already(player_id):
	for match_room in match_rooms:
		for player in (match_room.player1, match_room.player2):
			if player is not None and player_id == player.id:
				return True
	return False

def find_match_room_to_join(match_id):
	for match_room in match_rooms:
		if match_room.match_id == match_id and (match_room.player1 is None or match_room.player2 is None):
			pprint(f'Found match room: {match_room}')
			return match_room
	return None

# This functions orders the players in the room based on if they are player 1 or 2
@database_sync_to_async
def add_player_to_room(match_id, match_room, player_id, channel_name):
	match_database = get_object_or_404(Match, id=match_id)
	pprint(match_database.__dict__)
	pprint(f'player2_id: {match_database.player2_id} vs player_id: {player_id}')
	if match_database.player2_id == player_id:
		match_room.player2 = Player(player_id, channel_name)
	elif match_database.player1_id == player_id:
		pprint(f'Added player 1 with id {player_id} to match {match_id}')
		match_room.player1 = Player(player_id, channel_name)
	else:
		raise ValueError(f"Player ID {player_id} does not match any players in match {match_id}")

@database_sync_to_async
def set_user_state(user, userState):
	user.state = userState
	user.save(update_fields=["state"])

@database_sync_to_async
def set_match_status(match, matchStatus):
	match.status = matchStatus
	match.save(update_fields=['status'])

@database_sync_to_async
def set_match_winner(match):
	if match.player1_score > match.player2_score:
		match.winner = match.player1
	else:
		match.winner = match.player2
	match.status = Match.StatusOptions.FINISHED
	match.save(update_fields=['winner', 'status'])

@database_sync_to_async
def get_match_status(match_id):
	try:
		match = Match.objects.get(id=match_id)
		return (match.status)
	except Match.DoesNotExist:
		return None

class PongConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.id = self.scope['user'].id
		match_id = self.scope['url_route']['kwargs'].get('match_id')
		print(f"Player {self.id} is ready to play match {match_id}!")
		if is_player_in_match_room_already(self.id) or await (get_match_status(match_id)) == Match.StatusOptions.FINISHED:
			await self.close()
			return
		match_room = find_match_room_to_join(match_id)
		if not match_room:
			match_room = create_match_room(match_id)
		try:
			await add_player_to_room(match_id, match_room, self.id, self.channel_name)
		except ValueError:
			self.close()
			return
		self.match_group_name = match_room.match_id
		await self.channel_layer.group_add(
			self.match_group_name, 
			self.channel_name
		)
		await set_user_state(self.scope['user'], CustomUser.StateOptions.INGAME)
		await self.accept()
		print("Rooms after connect:")
		pprint(match_rooms)
		if (match_room.player1 is not None) and (match_room.player2 is not None):
			await self.play_pong(match_room)
		else:
			print("Waiting for more players to join the match room.")

	async def disconnect(self, close_code):
		await set_user_state(self.scope['user'], CustomUser.StateOptions.ONLINE)
		for match_room in match_rooms:
			if (match_room.player1 is not None) and (self.id == match_room.player1.id):
				match_room.player1 = None
			else:
				match_room.player2 = None
			await self.channel_layer.group_discard(
				self.match_group_name, self.channel_name
			)
			if match_room.player1 is None and match_room.player2 is None:
				match_rooms.remove(match_room)
			break
		print("Rooms after disconnect:")
		pprint(match_rooms)

	async def receive(self, text_data):
		text_data_json = json.loads(text_data)
		message = text_data_json["message"]
		print(f"Message in receive: {message}")

		# Send message to room group
		await self.channel_layer.group_send(
			self.match_group_name, {"type": "pong_message", "message": message}
		)
	
	async def pong_message(self, event):
		message = event["message"]
		#print(f"Received group message: {message}")
		await self.send(text_data=json.dumps({"message": message}))

	async def play_pong(self, match_room):
		match_database = await sync_to_async(get_object_or_404)(Match, id=match_room.match_id)
		await set_match_status(match_database, Match.StatusOptions.INPROGRESS)
		await self.channel_layer.group_send(
			self.match_group_name, {"type": "pong_message", "message": "pong game init"}
		)
		print(f"Starting game for: ")
		pprint(match_room)
		if match_database.player1_score > match_database.player2_score:
			highest_score = match_database.player1_score
		else:
			highest_score = match_database.player2_score
		while(highest_score < 5):
			random_value = random.randint(0, 1)
			if (random_value == 0):
				match_database.player1_score += 1
				await sync_to_async(match_database.save)(update_fields=["player1_score"])
				await self.channel_layer.group_send(
					self.match_group_name, {
						"type": "pong_message",
						"message": f"Player 1 scored, current score is {match_database.player1_score}:{match_database.player2_score}"
					}
				)
			else:
				match_database.player2_score += 1
				await sync_to_async(match_database.save)(update_fields=["player2_score"])
				await self.channel_layer.group_send(
					self.match_group_name, {
						"type": "pong_message",
						"message": f"Player 2 scored, current score is {match_database.player1_score}:{match_database.player2_score}"
					}
				)
			match_database = await sync_to_async(get_object_or_404)(Match, id=match_room.match_id)
			if match_database.player1_score > match_database.player2_score:
				highest_score = match_database.player1_score
			else:
				highest_score = match_database.player2_score
		await set_match_winner(match_database)
		# return await self.close() - should work when play_pong is implemented differently, for both players
			
