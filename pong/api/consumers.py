# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    consumers.py                                       :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: vbartos <vbartos@student.42prague.com>     +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/11/28 14:23:42 by plouda            #+#    #+#              #
#    Updated: 2024/12/05 12:58:32 by vbartos          ###   ########.fr        #
#                                                                              #
# **************************************************************************** #


from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import CustomUser, Match
from pprint import pprint # nice printing
import json
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async
import asyncio, logging
from .pong_collision import paddle_collision
import math
from .pong_collision import PongGame

match_rooms = []

from pprint import pprint

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
			logging.info(f"Player {self.id} in room already or connecting to a finished match")
			await self.close()
			return
		match_room = find_match_room_to_join(match_id)
		if not match_room:
			match_room = create_match_room(match_id)
		try:
			await add_player_to_room(match_id, match_room, self.id, self.channel_name)
		except ValueError:
			logging.info("VALUE ERROR")
			await self.close()
			return
		self.match_group_name = match_room.match_id
		await self.channel_layer.group_add(
			self.match_group_name, 
			self.channel_name
		)
		#await set_user_state(self.scope['user'], CustomUser.StateOptions.INGAME)
		await self.accept()
		print("Rooms after connect:")
		pprint(match_rooms)
		if (match_room.player1 is not None) and (match_room.player2 is not None):
			await self.play_pong(match_room)
		else:
			print("Waiting for more players to join the match room.")

	async def disconnect(self, close_code):
		await set_user_state(self.scope['user'], CustomUser.StateOptions.IDLE)
		for match_room in match_rooms:
			if (match_room.player1 is not None and match_room.player1.channel_name == self.channel_name) or (match_room.player2 is not None and match_room.player2.channel_name == self.channel_name):
				await self.channel_layer.group_discard(
					self.match_group_name, self.channel_name
				)
			if (match_room.player1 is not None) and (self.id == match_room.player1.id):
				match_room.player1 = None
			else:
				match_room.player2 = None
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
				"for_player" : event["for_player"],
				"sequence" : event["sequence"],
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

	async def move_paddle(self, paddle, direction):
		match_room = None
		for room in match_rooms:
			if room.match_id == self.match_group_name:
				match_room = room
		if not match_room:
			return
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
		await asyncio.sleep(0.01)

	async def play_pong(self, match_room):
		match_database = await sync_to_async(get_object_or_404)(Match, id=match_room.match_id)
		await set_match_status(match_database, Match.StatusOptions.INPROGRESS)
		await self.channel_layer.group_send(
			self.match_group_name, {
				"type": "match_start",
				"message": "match_start",
				"player1": match_room.player1.username,
				"player2": match_room.player2.username
			}
		)
		print(f"Starting game for: ")
		pprint(match_room)
		asyncio.create_task(self.game_loop(match_room, match_database))

	async def game_loop(self, match_room, match_database):
		await asyncio.sleep(3)
		sequence = 0
		ball = match_room.ball
		paddle1 = match_room.paddle1
		paddle2 = match_room.paddle2
		
		while 42:
			if match_room.player1 is None or match_room.player2 is None:
				break

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
				match_room.reset()
				ball = match_room.ball
				paddle1 = match_room.paddle1
				paddle2 = match_room.paddle2

			# Scoring player 1 - ball out of bounds on the right side
			if (ball_right >= (match_room.GAME_HALF_WIDTH)):
				match_room.player1.score += 1
				match_database.player1_score += 1
				await sync_to_async(match_database.save)(update_fields=["player1_score"])
				match_room.reset()
				ball = match_room.ball
				paddle1 = match_room.paddle1
				paddle2 = match_room.paddle2

			# Update ball position
			ball.position += ball.direction * ball.speed

			sequence += 1
			#logging.info(f"Sending draw message to player 1: {match_room.player1.channel_name}")
			await self.channel_layer.send(
				match_room.player1.channel_name, {
					"type": "draw",
					"message": "draw",
					"sequence": sequence,
					"for_player": match_room.player1.id,
					"ball_x": ball.position.x,
					"ball_y": ball.position.y,
					"paddle1_x": paddle1.position.x,
					"paddle1_y": paddle1.position.y,
					"paddle2_x": paddle2.position.x,
					"paddle2_y": paddle2.position.y,
					"player1_score": match_room.player1.score,
					"player2_score": match_room.player2.score
				}
			)

			#logging.info(f"Sending draw message to player 2: {match_room.player2.channel_name}")
			await self.channel_layer.send(
				match_room.player2.channel_name, {
					"type": "draw",
					"message": "draw",
					"sequence": sequence,
					"for_player": match_room.player1.id,
					"ball_x": ball.position.x,
					"ball_y": ball.position.y,
					"paddle1_x": paddle1.position.x,
					"paddle1_y": paddle1.position.y,
					"paddle2_x": paddle2.position.x,
					"paddle2_y": paddle2.position.y,
					"player1_score": match_room.player1.score,
					"player2_score": match_room.player2.score
				}
			)

			# Game over
			if match_database.player1_score >= 5 or match_database.player2_score >= 5:
				await set_match_winner(match_database)
				break

			# Short sleep
			await asyncio.sleep(0.1)
		await self.channel_layer.group_send(
				self.match_group_name, {
					"type" : "match_end",
					"message" : "match_end"
				}
			)