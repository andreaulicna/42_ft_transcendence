from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import CustomUser, AIMatch
from pprint import pprint # nice printing
import json
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async
import asyncio, logging
from .pong_collision import paddle_collision, ball_collision_point, ball_center_from_collision
import math
from .pong_collision import PongGame
import random
from django.utils import timezone
import time
from .utils import Vector2D, get_line_intersection
from ai_play.settings import GAME_CONSTANTS

match_rooms = []

from pprint import pprint

class Player:
	def __init__(self, player_id, username):
		self.id = player_id
		self.username = username
		self.score = 0

	def __repr__(self):
		return f"Player(id={self.id}, username={self.username})"
	
class Prediction:
	def __init__(self):
		self.direction = Vector2D(0, 0)
		self.position = Vector2D(0, 0)
		self.exact_position = Vector2D(0, 0)
		self.since = 0
		self.size = 0

class AILevel:
	def __init__(self, reaction, error):
		self.reaction = reaction
		self.error = error

	def __repr__(self):
		return f"AILevl(reaction={self.reaction}, error={self.error})"

# max_score = 5
		#	{"aiReaction": 0.1, "aiError":  60},  # 0: ai is losing by 4
		#	{"aiReaction": 0.2, "aiError":  70},  # 1: ai is losing by 3
		#	{"aiReaction": 0.3, "aiError":  80},  # 2: ai is losing by 2
		#	{"aiReaction": 0.4, "aiError":  90},  # 3: ai is losing by 1
		#	{"aiReaction": 0.5, "aiError":  100}, # 4: tie
		#	{"aiReaction": 0.6, "aiError": 110},  # 5: ai is winning by 1
		#	{"aiReaction": 0.7, "aiError": 120},  # 6: ai is winning by 2
		#	{"aiReaction": 0.8, "aiError": 130},  # 7: ai is winning by 3
		#	{"aiReaction": 0.9, "aiError": 140},  # 8: ai is winning by 4

# max_score = 3
		#	{"aiReaction": 0.1, "aiError":  60},  # 0: ai is losing by 2
		#	{"aiReaction": 0.2, "aiError":  70},  # 1: ai is losing by 1
		#	{"aiReaction": 0.3, "aiError":  80},  # 2: tie
		#	{"aiReaction": 0.4, "aiError":  90},  # 3: ai is winning by 1
		#	{"aiReaction": 0.5, "aiError":  100}, # 4: winning by 2

class AIPlayer:
	def __init__(self, level):
		self.levels = []
		self.levels = self.set_initial_levels(level)
		self.level = self.levels[level - 1]
		self.username = "AI"
		self.score = 0
		self.prediction = None

	def predict(self, dt, ball, paddle, match_room):
		# only re-predict if the ball changed direction, or its been some amount of time since last prediction
		if (
			self.prediction and self.prediction.position and
			(self.prediction.direction.x * ball.direction.x) > 0 and
			(self.prediction.direction.y * ball.direction.y) > 0 and
			(self.prediction.since < self.level.reaction)
		):
			self.prediction.since += dt
			return
		self.prediction = Prediction()
		paddle_left = paddle.position.x - paddle.paddle_half_width
		# assume collision point on ball_left
		collision_point = Vector2D(ball.position.x + (ball.size / 2), ball.position.y)
		#collision_point = ball_collision_point(ball)
		far_collision_point = collision_point + (ball.direction * 10000) # QUESTION - is such an arbitrary number ok?
		
		pt = get_line_intersection(paddle_left, -10000, paddle_left, 10000, collision_point.x, collision_point.y, far_collision_point.x, far_collision_point.y)
		
		if (pt):
			# logging.info(f"Prediction exact: {pt}")
			#pt = ball_center_from_collision(pt, ball.direction, ball.size)
			# adjust back from ball_left
			pt.x -= (ball.size / 2)
			# logging.info(f"Prediction exact adjusted: {pt}")
			court_top = match_room.GAME_HALF_HEIGHT * (-1) + ball.size / 2
			court_bottom = match_room.GAME_HALF_HEIGHT - ball.size / 2
			while pt.y < court_top or pt.y > court_bottom:
				if pt.y < court_top:
					pt.y = court_top + (court_top - pt.y)
				elif pt.y > court_bottom:
					pt.y = court_bottom - (pt.y - court_bottom)
			self.prediction.exact_position = pt

			if (ball.direction.x < 0):
				closeness = (ball.position.x - paddle_left) / match_room.GAME_WIDTH
			else:
				closeness = (paddle_left - ball.position.x) / match_room.GAME_WIDTH
			error = self.level.error * closeness
			self.prediction.position = Vector2D(pt.x, pt.y + random.uniform(-error, error))
			self.prediction.since = 0
			self.prediction.direction = ball.direction
			logging.info(f"AI prediction: {self.prediction.position}")
		else:
			self.position = Vector2D(0, 0)
			self.exact_position = Vector2D(0, 0)
	#		logging.info("No prediction made.")

	def move_ai_paddle(self, paddle, match_room):
		if not self.prediction.position:
			return

		if self.prediction.position.y < paddle.position.y - paddle.paddle_half_height:
			if paddle.position.y > (match_room.GAME_HALF_HEIGHT - paddle.paddle_half_height) * (-1):
				paddle.position.y -= paddle.paddle_speed
		elif self.prediction.position.y > paddle.position.y + paddle.paddle_half_height:
			if paddle.position.y < (match_room.GAME_HALF_HEIGHT - paddle.paddle_half_height):
				paddle.position.y += paddle.paddle_speed

	def set_initial_levels(self, max_score):
		levels = []
		reaction = 0
		reaction_increment = 0.1
		error = 50
		error_increment = 10
		num_of_levels = (max_score - 1) * 2 + 1
		while (num_of_levels > 0):
			new_level = AILevel(reaction + reaction_increment, error + error_increment)
			reaction += reaction_increment
			error += error_increment
			levels.append(new_level)
			num_of_levels -= 1
		#logging.info(f"Setting these levels: {levels}")
		return levels

	def update_level(self, ai_player_score, other_player_score):
		if (ai_player_score == GAME_CONSTANTS['MAX_SCORE'] or other_player_score == GAME_CONSTANTS['MAX_SCORE']):
			return
		neutral_level = (len(self.levels) // 2) # integer division to avoid indexing with floats
		# logging.info(f"Neutral level: {neutral_level}") # should be the level in the middle
		if ai_player_score == other_player_score:
			self.level = self.levels[neutral_level]
		elif ai_player_score > other_player_score:
			self.level = self.levels[neutral_level + (ai_player_score - other_player_score)]
		elif ai_player_score < other_player_score:
			self.level = self.levels[neutral_level - (other_player_score - ai_player_score)]

	def __repr__(self):
		return f"AIPlayer (username={self.username}, levels={self.levels})"


@database_sync_to_async
def create_match_room(match_id, player_id):
	match_database = get_object_or_404(AIMatch, id=match_id)
	if match_database.creator.id == player_id:
		logging.info(f'Added creator with id {player_id} to match {match_id}')
		player1 = Player(player_id, match_database.creator.username)
		player2 = AIPlayer(3)
	else:
		raise ValueError(f"Player ID {player_id} does not match any players in match {match_id}")

	match_room = PongGame(match_id, player1, player2)
	match_rooms.append(match_room)
	return match_room

def is_player_in_match_room_already(player_id):
	for match_room in match_rooms:
		if match_room.player1 is not None and match_room.player1.id == player_id:
			return True
	return False

def find_player_in_match_room(player_id):
	for match_room in match_rooms:
		if (match_room.player1 is not None and match_room.player1.id == player_id):
			return match_room
	return None

@database_sync_to_async
def set_user_state(user, userState):
	user.state = userState
	user.save(update_fields=["state"])

@database_sync_to_async
def set_match_status(match, matchStatus):
	match.status = matchStatus
	match.save(update_fields=['status'])

@database_sync_to_async
def set_match_winner(match_database):
	if match_database.player1_score > match_database.player2_score:
		match_database.winner = match_database.creator.username
	else:
		match_database.winner = "AI"
	match_database.status = AIMatch.StatusOptions.FINISHED
	match_database.save(update_fields=['winner', 'status'])

@database_sync_to_async
def get_match_status(match_id):
	try:
		match = AIMatch.objects.get(id=match_id)
		return (match.status)
	except AIMatch.DoesNotExist:
		return None

class AIPlayConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.id = self.scope['user'].id
		match_id = self.scope['url_route']['kwargs'].get('match_id')
		logging.info(f"Player {self.id} is ready to play match {match_id}!")
		if is_player_in_match_room_already(self.id) or await (get_match_status(match_id)) == AIMatch.StatusOptions.FINISHED:
			logging.info(f"Player {self.id} in room already or connecting to a finished match")
			await self.close()
			return
		try:
			match_room = await create_match_room(match_id, self.id)
		except ValueError:
			logging.info("VALUE ERROR")
			await self.close()
			return
		await self.accept()
		logging.info("Rooms after connect:")
		logging.info(match_rooms)
		if (match_room.player1 is not None):
			await self.play_pong(match_room)

	async def disconnect(self, close_code):
		logging.info(f"Disconnecting player {self.id} from pong")
		await set_user_state(self.scope['user'], CustomUser.StateOptions.IDLE)
		for match_room in match_rooms:
			if (match_room.player1 is not None) and (self.id == match_room.player1.id):
				match_room.player1 = None
				match_rooms.remove(match_room)
				break
		logging.info("Rooms after disconnect:")
		logging.info(match_rooms)

	async def receive(self, text_data):
		text_data_json = json.loads(text_data)
		message_type = text_data_json["type"]
		paddle = text_data_json["paddle"]

		if message_type == "paddle_movement":
			match_room = find_player_in_match_room(self.id)
			if not match_room:
				return
			direction = text_data_json["direction"]
			await self.move_paddle(match_room, paddle, direction)
	
	async def draw(self, event):
		await self.send(text_data=json.dumps(
			{
				"type": event["message"],
				"for_player" : event["for_player"],
				"sequence" : event["sequence"],
				"ball_x": event["ball_x"],
				"ball_y": event["ball_y"],
				"ball_exact_prediction_x": event["ball_exact_prediction_x"],
				"ball_exact_prediction_y": event["ball_exact_prediction_y"],
				"ball_prediction_x": event["ball_prediction_x"],
				"ball_prediction_y": event["ball_prediction_y"],
				"paddle1_x": event["paddle1_x"],
				"paddle1_y": event["paddle1_y"],
				"paddle2_x": event["paddle2_x"],
				"paddle2_y": event["paddle2_y"],
				"player1_score": event["player1_score"],
				"player2_score": event["player2_score"]
			}
		))

	async def match_start(self, event):
		logging.info("match_start called")
		await self.send(text_data=json.dumps(
			{
				"type": event["message"],
				"player1": event["player1"],
				"player2": event["player2"]
			}
		))

	async def match_end(self, event):
		logging.info("match_end called")
		await self.send(text_data=json.dumps(
			{
				"type": event["message"]
			}
		))
		await self.close()

	async def move_paddle(self, match_room, paddle, direction):
		paddle_speed = match_room.PADDLE_SPEED
		if paddle == "paddle1":
			if direction == "UP" and match_room.paddle1.position.y > (match_room.GAME_HALF_HEIGHT - match_room.paddle1.paddle_half_height) * (-1):
				match_room.paddle1.position.y -= paddle_speed
			elif direction == "DOWN" and match_room.paddle1.position.y < (match_room.GAME_HALF_HEIGHT - match_room.paddle1.paddle_half_height):
				match_room.paddle1.position.y += paddle_speed
		elif paddle == "paddle2":
			if direction == "UP" and match_room.paddle2.position.y > (match_room.GAME_HALF_HEIGHT - match_room.paddle2.paddle_half_height) * (-1):
				match_room.paddle2.position.y -= paddle_speed
			elif direction == "DOWN" and match_room.paddle2.position.y < (match_room.GAME_HALF_HEIGHT - match_room.paddle2.paddle_half_height):
				match_room.paddle2.position.y += paddle_speed

	async def play_pong(self, match_room):
		match_database = await sync_to_async(get_object_or_404)(AIMatch, id=match_room.match_id)
		await set_match_status(match_database, AIMatch.StatusOptions.INPROGRESS)
		await self.send(text_data=json.dumps(
			{
				"type": "match_start",
				"message": "match_start",
				"player1": match_room.player1.username,
				"player2": match_room.player2.username
			}
		))
		logging.info(f"Starting game for: ")
		logging.info(match_room)
		asyncio.create_task(self.game_loop(match_room, match_database))

	async def game_loop(self, match_room, match_database):
		await asyncio.sleep(3)
		sequence = 0
		ball = match_room.ball
		paddle1 = match_room.paddle1
		paddle2 = match_room.paddle2
		ai_player = match_room.player2
		
		while 42:
			if match_room.player1 is None:
				break

			match_room.start_timestamp = timezone.now()
			dt = (match_room.start_timestamp - match_room.last_frame).total_seconds()
			ai_player.predict(dt, ball, paddle2, match_room)
			ai_player.move_ai_paddle(paddle2, match_room)

			# Ball collision with floor & ceiling
			if (ball.position.y > (match_room.GAME_HALF_HEIGHT - (ball.size / 2))) or ((ball.position.y < ((match_room.GAME_HALF_HEIGHT - (ball.size / 2))) * (-1))):
				ball.direction.y *= -1

			# might be a source of bugs, watch out
			ball = paddle_collision(ball, paddle1, paddle2)
			ball_right = ball.position.x + (ball.size / 2)
			ball_left = ball.position.x - (ball.size / 2)

			# Scoring player 2 - ball out of bounds on the left side
			if (ball_left <= (0 - match_room.GAME_HALF_WIDTH)):
				match_room.player2.score += 1
				match_database.player2_score += 1
				await sync_to_async(match_database.save)(update_fields=["player2_score"])
				ai_player.update_level(ai_player.score, match_room.player1.score)
				match_room.reset()
				ball = match_room.ball
				paddle1 = match_room.paddle1
				paddle2 = match_room.paddle2

			# Scoring player 1 - ball out of bounds on the right side
			if (ball_right >= (match_room.GAME_HALF_WIDTH)):
				match_room.player1.score += 1
				match_database.player1_score += 1
				await sync_to_async(match_database.save)(update_fields=["player1_score"])
				ai_player.update_level(ai_player.score, match_room.player1.score)
				match_room.reset()
				ball = match_room.ball
				paddle1 = match_room.paddle1
				paddle2 = match_room.paddle2

			# Update ball position
			ball.position += ball.direction * ball.speed

			sequence += 1
			#logging.info(f"Sending draw message to player 1: {match_room.player1.channel_name}")
			await self.send(text_data=json.dumps(
				{
					"type": "draw",
					"message": "draw",
					"sequence": sequence,
					"for_player": match_room.player1.id,
					"ball_x": ball.position.x,
					"ball_y": ball.position.y,
					"ball_exact_prediction_x": ai_player.prediction.exact_position.x,
					"ball_exact_prediction_y": ai_player.prediction.exact_position.y,
					"ball_prediction_x": ai_player.prediction.position.x,
					"ball_prediction_y": ai_player.prediction.position.y,
					"paddle1_x": paddle1.position.x,
					"paddle1_y": paddle1.position.y,
					"paddle2_x": paddle2.position.x,
					"paddle2_y": paddle2.position.y,
					"player1_score": match_room.player1.score,
					"player2_score": match_room.player2.score
				}
			))

			# Game over
			if match_database.player1_score >= GAME_CONSTANTS['MAX_SCORE'] or match_database.player2_score >= GAME_CONSTANTS['MAX_SCORE']:
				await set_match_winner(match_database)
				break
			match_room.last_frame = match_room.start_timestamp

			# Short sleep
			await asyncio.sleep(0.01)
		logging.info(f"Match end for AI match {match_room.match_id}")
		await self.match_end(
			{
					"type" : "match_end",
					"message" : "match_end"
			}
		)