from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import CustomUser, Match
from pprint import pprint # nice printing
import json
from django.shortcuts import get_object_or_404
import random
from asgiref.sync import sync_to_async
import asyncio

match_rooms = []

from pprint import pprint

class PongGame:
	def __init__(self, match_id):
		self.match_id = match_id
		self.game_width = 160
		self.game_height = 100
		self.game_half_width = self.game_width / 2
		self.game_half_height = self.game_height / 2
		self.default_paddle_height = self.game_height / (10 * 2)  # adjusted for a half
		self.default_paddle_width = 2 / 2  # adjusted for a half
		self.default_paddle_speed = 5
		self.paddle1 = Paddle(x=-80 + self.default_paddle_width, game=self)
		self.paddle2 = Paddle(x=80 - self.default_paddle_width, game=self)
		self.ball = Ball()
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
		self.paddle_speed = game.default_paddle_speed

	def __repr__(self):
		return f"Paddle(x={self.x}, y={self.y}, paddle_height={self.paddle_height}, paddle_width={self.paddle_width}, paddle_speed={self.paddle_speed})"

class Ball:
	def __init__(self):
		self.x = 0
		self.y = 0
		self.speed = 1
		self.x_direction = random.choice([-1, 1])
		self.y_direction = random.choice([-1, 1])
		self.size = 1
	
	def __repr__(self):
		return f"Ball(x={self.x}, y={self.y}, speed={self.speed})"

class Player:
	def __init__(self, player_id, channel_name, username):
		self.id = player_id
		self.channel_name = channel_name
		self.username = username
		self.score = 0

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

def find_player_in_match_room(player_id):
	for match_room in match_rooms:
		if match_room.player1.id == player_id or match_room.player2.id == player_id:
			return match_room
	return None

#@database_sync_to_async
#def get_player_username(player_id):
#	player = get_object_or_404(Player, id=player_id)
#	return (player.username)

# This functions orders the players in the room based on if they are player 1 or 2
@database_sync_to_async
def add_player_to_room(match_id, match_room, player_id, channel_name):
	match_database = get_object_or_404(Match, id=match_id)
	pprint(match_database.__dict__)
	pprint(f'player2_id: {match_database.player2_id} vs player_id: {player_id}')
	if match_database.player2_id == player_id:
		match_room.player2 = Player(player_id, channel_name, "user1")
	elif match_database.player1_id == player_id:
		pprint(f'Added player 1 with id {player_id} to match {match_id}')
		match_room.player1 = Player(player_id, channel_name, "user2")
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
			if (match_room.player1 is None) and (match_room.player2 is None):
				match_rooms.remove(match_room)
			break
		print("Rooms after disconnect:")
		pprint(match_rooms)

	async def receive(self, text_data):
		text_data_json = json.loads(text_data)
		message_type = text_data_json["type"]

		if message_type == "paddle_movement":
			match_room = find_player_in_match_room(self.id)
			if not match_room:
				return
			if match_room.player1.id == self.id:
				paddle = "paddle1"
			elif match_room.player2.id == self.id:
				paddle = "paddle2"
			direction = text_data_json["direction"]
			await self.move_paddle(paddle, direction)
	
	async def draw(self, event):
		await self.send(text_data=json.dumps(
			{
				"type": event["message"],
				"ball_x": event["ball_x"],
				"ball_y": event["ball_y"],
				"paddle1_x": event["paddle1_x"],
				"paddle1_y": event["paddle1_y"],
				"paddle2_x": event["paddle2_x"],
				"paddle2_y": event["paddle2_y"],
				"player1_score": event["player1_score"],
				"player2_score": event["player2_score"]
			}
		))

	async def match_start(self, event):
		await self.send(text_data=json.dumps(
			{
				"type": event["message"],
				"player1": event["player1"],
				"player2": event["player2"]
			}
		))

	async def move_paddle(self, paddle, direction):
		match_room = None
		for room in match_rooms:
			if room.match_id == self.match_group_name:
				match_room = room
		if not match_room:
			return
		paddle_speed = match_room.default_paddle_speed
		if paddle == "paddle1":
			if direction == "UP" and match_room.paddle1.y < (match_room.game_half_height - match_room.paddle1.paddle_height):
				match_room.paddle1.y += paddle_speed
			elif direction == "DOWN" and match_room.paddle1.y > (match_room.game_half_height - match_room.paddle1.paddle_height) * (-1):
				match_room.paddle1.y -= paddle_speed
		elif paddle == "paddle2":
			if direction == "UP" and match_room.paddle2.y < (match_room.game_half_height - match_room.paddle2.paddle_height):
				match_room.paddle2.y += paddle_speed
			elif direction == "DOWN" and match_room.paddle2.y > (match_room.game_half_height - match_room.paddle2.paddle_height) * (-1):
				match_room.paddle2.y -= paddle_speed
		await self.channel_layer.group_send(
			self.match_group_name, {
				"type": "draw",
				"message": "draw",
				"ball_x": match_room.ball.x,
				"ball_y": match_room.ball.y,
				"paddle1_x" : match_room.paddle1.x, 
				"paddle1_y" : match_room.paddle1.y,
				"paddle2_x" : match_room.paddle2.x,
				"paddle2_y" : match_room.paddle2.y,
				"player1_score": match_room.player1.score,
				"player2_score": match_room.player2.score
			}
		)

	async def play_pong(self, match_room):
		match_database = await sync_to_async(get_object_or_404)(Match, id=match_room.match_id)
		await set_match_status(match_database, Match.StatusOptions.INPROGRESS)
		await self.channel_layer.group_send(
			self.match_group_name, {
				"type": "match_start",
				"message": "match_start",
				"player1": match_room.player1.username,
				"player2": match_room.player1.username
			}
		)
		print(f"Starting game for: ")
		pprint(match_room)

		ball = match_room.ball
		paddle1 = match_room.paddle1
		paddle2 = match_room.paddle2
		
		while 42:
			# Update ball position
			ball.x += ball.speed * ball.x_direction
			ball.y += ball.speed * ball.y_direction

			# Ball collision with floor & ceiling
			if (ball.y <= (match_room.game_half_height - ball.size)) or ((ball.y >= match_room.game_half_height - ball.size) * (-1)):
				ball.y_direction *= -1
			
			# Ball collision with paddles
			paddle1_top = paddle1.y + paddle1.paddle_height
			paddle1_bottom = paddle1.y - paddle1.paddle_height
			paddle1_right = paddle1.x + paddle1.paddle_width
			ball_left = ball.x + ball.size
			if (ball_left <= paddle1_right) and (paddle1_bottom <= ball.y <= paddle1_top):
				ball.x_direction *= -1
				ball.speed += 1

			paddle2_top = paddle2.y + paddle2.paddle_height
			paddle2_bottom = paddle2.y - paddle2.paddle_height
			paddle2_left = paddle2.x - paddle2.paddle_width
			ball_right = ball.x + ball.size
			if (ball_right >= paddle2_left) and (paddle2_bottom <= ball.y <= paddle2_top):
				ball.x_direction *= -1
				ball.speed += 1

			# Scoring - player1
			if (ball_left <= (0 - match_room.game_half_width)):
				random_value = random.randint(0, 1)
				if (random_value == 0):
					match_room.player1.score += 1
					match_database.player1_score += 1
					await sync_to_async(match_database.save)(update_fields=["player1_score"])
			
			# Scoring - player2
			if (ball_right >= (match_room.game_half_width)):
				random_value = random.randint(0, 1)
				if (random_value == 0):
					match_room.player2.score += 1
					match_database.player2_score += 1
					await sync_to_async(match_database.save)(update_fields=["player2_score"])

			# Match state group send
			await self.channel_layer.group_send(
				self.match_group_name, {
					"type" : "draw",
					"message": "draw",
					"ball_x" : ball.x,
					"ball_y" : ball.y,
					"paddle1_x" : paddle1.x, 
					"paddle1_y" : paddle1.y,
					"paddle2_x" : paddle2.x, 
					"paddle2_y" : paddle2.y,
					"player1_score": match_room.player1.score,
					"player2_score": match_room.player2.score
				}
			)

			# Game over
			if match_database.player1_score >= 5 or match_database.player2_score >= 5:
				await set_match_winner(match_database)
				break

			# Short sleep
			await asyncio.sleep(0.01)

	
	#	RANDOM SCORING LOOP	
	#	match_database = await sync_to_async(get_object_or_404)(Match, id=match_room.match_id)
	#	await set_match_status(match_database, Match.StatusOptions.INPROGRESS)
	#	await self.channel_layer.group_send(
	#		self.match_group_name, {"type": "pong_message", "message": "pong game init"}
	#	)
	#	print(f"Starting game for: ")
	#	pprint(match_room)
	#	if match_database.player1_score > match_database.player2_score:
	#		highest_score = match_database.player1_score
	#	else:
	#		highest_score = match_database.player2_score
	#	while(highest_score < 5):
	#		random_value = random.randint(0, 1)
	#		if (random_value == 0):
	#			match_database.player1_score += 1
	#			await sync_to_async(match_database.save)(update_fields=["player1_score"])
	#			await self.channel_layer.group_send(
	#				self.match_group_name, {
	#					"type": "pong_message",
	#					"message": f"Player 1 scored, current score is {match_database.player1_score}:{match_database.player2_score}"
	#				}
	#			)
	#		else:
	#			match_database.player2_score += 1
	#			await sync_to_async(match_database.save)(update_fields=["player2_score"])
	#			await self.channel_layer.group_send(
	#				self.match_group_name, {
	#					"type": "pong_message",
	#					"message": f"Player 2 scored, current score is {match_database.player1_score}:{match_database.player2_score}"
	#				}
	#			)
	#		match_database = await sync_to_async(get_object_or_404)(Match, id=match_room.match_id)
	#		if match_database.player1_score > match_database.player2_score:
	#			highest_score = match_database.player1_score
	#		else:
	#			highest_score = match_database.player2_score
	#	await set_match_winner(match_database)
	#	# return await self.close() - should work when play_pong is implemented differently, for both players