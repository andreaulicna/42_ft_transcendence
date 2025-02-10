from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import CustomUser, AIMatch
from pprint import pprint # nice printing
import json
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async
import asyncio, logging
from .pong_collision import paddle_collision
import math
from .pong_collision import PongGame
import random
from django.utils import timezone
import time
from .utils import Vector2D, get_line_intersection
from ai_play.settings import GAME_CONSTANTS

match_rooms = []

from pprint import pprint

@database_sync_to_async
def create_match_room(match_id, player_id):
	match_database = get_object_or_404(AIMatch, id=match_id)
	if match_database.creator.id == player_id:
		#logging.info(f'Added creator with id {player_id} to match {match_id}')
		match_room = PongGame(match_id, player_id, match_database.creator.username)
		match_rooms.append(match_room)
	else:
		raise ValueError(f"Player ID {player_id} does not match any players in match {match_id}")

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
	elif match_database.player2_score > match_database.player1_score:
		match_database.winner = "AI"
	else:
		match_database.winner = ""
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
			#logging.info(f"Player {self.id} in room already or connecting to a finished match")
			await self.close()
			return
		try:
			match_room = await create_match_room(match_id, self.id)
		except ValueError:
			await self.close()
			return
		await self.accept()
		await set_user_state(self.scope['user'], CustomUser.StateOptions.INGAME)
		logging.info("Rooms after connect:")
		logging.info(match_rooms)
		if (match_room.player1 is not None):
			await self.play_pong(match_room)

	async def disconnect(self, close_code):
		match_room = find_player_in_match_room(self.id)
		match_id = self.scope['url_route']['kwargs'].get('match_id')
		if match_room.match_id == match_id:
			#logging.info(f"Disconnecting player {self.id} from ai_play")
			await set_user_state(self.scope['user'], CustomUser.StateOptions.IDLE)
			for match_room in match_rooms:
				if (match_room.player1 is not None) and (self.id == match_room.player1.id):
					match_room.player1 = None
					match_rooms.remove(match_room)
					break
			logging.info("Rooms after disconnect:")
			logging.info(match_rooms)

	async def receive(self, text_data):
		try:
			text_data_json = json.loads(text_data)
		except json.JSONDecodeError:
			# Handle the case where the JSON is invalid
			self.send(text_data=json.dumps({
				"error": "Invalid JSON format."
			}))
			return
		
		if "type" in text_data_json:
			message_type = text_data_json["type"]

			if message_type == "paddle_movement":
				paddle = text_data_json["paddle"]
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
				#"ball_exact_prediction_x": event["ball_exact_prediction_x"],
				#"ball_exact_prediction_y": event["ball_exact_prediction_y"],
				#"ball_prediction_x": event["ball_prediction_x"],
				#"ball_prediction_y": event["ball_prediction_y"],
				"paddle1_x": event["paddle1_x"],
				"paddle1_y": event["paddle1_y"],
				"paddle2_x": event["paddle2_x"],
				"paddle2_y": event["paddle2_y"],
				"player1_score": event["player1_score"],
				"player2_score": event["player2_score"]
			}
		))

	async def match_start(self, event):
		#logging.info("match_start called")
		await self.send(text_data=json.dumps(
			{
				"type": event["message"],
				"player1": event["player1"],
				"player2": event["player2"],
				"ball_x": event["ball_x"],
				"ball_y": event["ball_y"],
				# "ball_exact_prediction_x": event["ball_exact_prediction_x"],
				# "ball_exact_prediction_y": event["ball_exact_prediction_y"],
				# "ball_prediction_x": event["ball_prediction_x"],
				# "ball_prediction_y": event["ball_prediction_y"],
				"paddle1_x": event["paddle1_x"],
				"paddle1_y": event["paddle1_y"],
				"paddle2_x": event["paddle2_x"],
				"paddle2_y": event["paddle2_y"],
				"player1_score": event["player1_score"],
				"player2_score": event["player2_score"],
				"game_start" : event["game_start"]
			}
		))

	async def match_end(self, event):
		#logging.info("match_end called")
		await self.send(text_data=json.dumps(
			{
				"type": event["message"],
				"winner_username" : event["winner_username"]
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
				"player2": match_room.player2.username,
				"ball_x": match_room.ball.position.x,
				"ball_y": match_room.ball.position.y,
				# "ball_exact_prediction_x": match_room.player2.prediction.exact_position.x,
				# "ball_exact_prediction_y": match_room.player2.prediction.exact_position.y,
				# "ball_prediction_x": match_room.player2.prediction.position.x,
				# "ball_prediction_y": match_room.player2.prediction.position.y,
				"paddle1_x": match_room.paddle1.position.x,
				"paddle1_y": match_room.paddle1.position.y,
				"paddle2_x": match_room.paddle2.position.x,
				"paddle2_y": match_room.paddle2.position.y,
				"player1_score": match_room.player1.score,
				"player2_score": match_room.player2.score,
				"game_start" : match_room.set_game_start_time(seconds_to_start=5).isoformat()
			}
		))
		logging.info(f"Starting game for: ")
		logging.info(match_room)
		asyncio.create_task(self.game_loop(match_room, match_database))

	async def game_loop(self, match_room, match_database):
		#logging.info(f"Game will start in: {match_room.get_seconds_until_game_start()} seconds")
		await asyncio.sleep(match_room.get_seconds_until_game_start())
		sequence = 0
		ball = match_room.ball
		paddle1 = match_room.paddle1
		paddle2 = match_room.paddle2
		ai_player = match_room.player2
		scored = False
		
		while 42:
			if match_room.player1 is None:
				await set_match_winner(match_database)
				break
			if scored == True:
				scored = False
				await asyncio.sleep(0.7)

			match_room.start_timestamp = timezone.now()
			dt = (match_room.start_timestamp - match_room.last_frame).total_seconds()
			ai_player.predict(dt, ball, paddle2, match_room)
			if sequence % 2 == 0:
				ai_player.move_ai_paddle(paddle2, match_room)

			# # Ball collision with floor & ceiling
			# if (ball.position.y > (match_room.GAME_HALF_HEIGHT - (ball.size / 2))) or ((ball.position.y < ((match_room.GAME_HALF_HEIGHT - (ball.size / 2))) * (-1))):
			# 	ball.direction.y *= -1
			if ball.position.y > (match_room.GAME_HALF_HEIGHT - (ball.size / 2)):
				if ball.direction.y > 0:
					ball.direction.y *= -1
			elif ball.position.y < ((match_room.GAME_HALF_HEIGHT - (ball.size / 2))) * (-1):
				if ball.direction.y < 0:
					ball.direction.y *= -1

			# might be a source of bugs, watch out
			ball = paddle_collision(ball, paddle1, paddle2, ai_player)
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
				scored = True

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
				scored = True

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
					#"ball_exact_prediction_x": ai_player.prediction.exact_position.x,
					#"ball_exact_prediction_y": ai_player.prediction.exact_position.y,
					#"ball_prediction_x": ai_player.prediction.position.x,
					#"ball_prediction_y": ai_player.prediction.position.y,
					"paddle1_x": paddle1.position.x,
					"paddle1_y": paddle1.position.y,
					"paddle2_x": paddle2.position.x,
					"paddle2_y": paddle2.position.y,
					"player1_score": match_room.player1.score,
					"player2_score": match_room.player2.score
				}
			))

			# Game over - we can break the loop only after the game state (coordinates in the above send) has been reset
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
					"message" : "match_end",
					"winner_username" : match_database.winner
			}
		)