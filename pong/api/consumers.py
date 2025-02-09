from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from channels.db import database_sync_to_async
from .models import CustomUser, Match
import json
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async
import asyncio, logging
from .pong_collision import paddle_collision
from .pong_collision import PongGame
import uuid # unique room_id
from asgiref.sync import async_to_sync
from pong.settings import GAME_CONSTANTS
from .serializers import MatchSerializer

matchmaking_rooms = [] # matchmaking rooms
rematch_rooms = [] # matchmaking rematch rooms
pong_rooms = [] # pong rooms
grace_period_dict = {}


#######################
# MATCHMAKING classes #
#######################

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

################################
# MATCHMAKING helper functions #
################################

def create_matchmaking_room():
	room = MatchRoom()
	matchmaking_rooms.append(room)
	return room

def create_rematch_room(prev_match_id):
	room = MatchRoom(prev_match_id=prev_match_id)
	rematch_rooms.append(room)
	return room

def add_player_to_matchmaking_room(room: MatchRoom, player_id, channel_name):
	if room.player1 is None:
		room.player1 = Player(player_id, channel_name)
	elif room.player2 is None:
		room.player2 = Player(player_id, channel_name)

def find_room_to_join():
	for room in matchmaking_rooms:
		if room.player1 is None or room.player2 is None:
			logging.info(f'Found match room: {room}')
			return room
	return None

def find_rematch_room_to_join(prev_match_id):
	for room in rematch_rooms:
		if room.room_id == str(prev_match_id):
			return room
	return None

def is_player_in_matchmaking_or_rematch_room_already(player_id) -> bool:
	for room in matchmaking_rooms + rematch_rooms:
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

def player_in_prev_match(prev_match, player_id):
	logging.info(f"Prev match_id: {prev_match}")
	logging.info(f"Prev match players: {prev_match.player1}, {prev_match.player2}")
	if prev_match is not None:
		if player_id in [prev_match.player1.id, prev_match.player2.id]:
			return True
	return False

def set_match_data(player1_id, player2_id):
	data = {
			'player1' : player1_id,
			'player2' : player2_id,
			'default_ball_size' : GAME_CONSTANTS['BALL_SIZE'],
			'default_paddle_height' : GAME_CONSTANTS['PADDLE_HEIGHT'],
			'default_paddle_width' : GAME_CONSTANTS['PADDLE_WIDTH'],
			'default_paddle_speed' : GAME_CONSTANTS['PADDLE_SPEED']
		}
	return data
	
def set_user_state_sync(user, state):
	user.state = state
	user.save(update_fields=["state"])

################
# PONG classes #
################

class Player:
	def __init__(self, player_id, channel_name):
		self.id = player_id
		self.channel_name = channel_name
		self.score = 0

	def __repr__(self):
		return f"Player(id={self.id}, channel_name={self.channel_name})"

#########################
# PONG helper functions #
#########################

def create_pong_room(match_id):
	pong_room = PongGame(match_id)
	pong_rooms.append(pong_room)
	return pong_room

def is_player_in_pong_room_already(player_id):
	for pong_room in pong_rooms:
		for player in (pong_room.player1, pong_room.player2):
			if player is not None and player_id == player.id:
				return True
	return False

def find_pong_room_to_join(match_id):
	for pong_room in pong_rooms:
		if pong_room.match_id == match_id and (pong_room.player1 is None or pong_room.player2 is None):
			logging.info(f'Found match room: {pong_room}')
			return pong_room
	return None

def find_player_in_pong_room(player_id):
	for pong_room in pong_rooms:
		if (pong_room.player1 is not None and pong_room.player1.id == player_id) or (pong_room.player2 is not None and pong_room.player2.id == player_id):
			return pong_room
	return None

# This functions orders the players in the room based on if they are player 1 or 2
@database_sync_to_async
def add_player_to_pong_room(match_id, pong_room, player_id, channel_name):
	match_database = get_object_or_404(Match, id=match_id)
	#logging.info(match_database.__dict__)
	if match_database.player2_id == player_id:
		logging.info(f'Added player 2 with id {player_id} to match {match_id}')
		pong_room.player2 = Player(player_id, channel_name)
	elif match_database.player1_id == player_id:
		logging.info(f'Added player 1 with id {player_id} to match {match_id}')
		pong_room.player1 = Player(player_id, channel_name)
	else:
		raise ValueError(f"Player ID {player_id} does not match any players in match {match_id}")

@database_sync_to_async
def set_user_state(user, state):
	user.state = state
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
def set_match_winner_on_dc(match, pong_room):
	if pong_room.player1 is None:
		match.winner = match.player2
		match.status = Match.StatusOptions.FINISHED
		match.save(update_fields=['winner', 'status'])
	elif pong_room.player2 is None:
		match.winner = match.player1
		match.status = Match.StatusOptions.FINISHED
		match.save(update_fields=['winner', 'status'])

@database_sync_to_async
def set_match_to_tie(match):
	match.winner = None
	match.status = Match.StatusOptions.FINISHED
	match.save(update_fields=['winner', 'status'])

@database_sync_to_async
def get_match_status(match_id):
	try:
		match = Match.objects.get(id=match_id)
		return (match.status)
	except Match.DoesNotExist:
		return None

@database_sync_to_async
def get_match_winner(match_id):
	try:
		match = Match.objects.get(id=match_id)
		return (match.winner)
	except Match.DoesNotExist:
		return None


########################
# MATCHMAKING Consumer #
########################

class MatchmakingConsumer(WebsocketConsumer):
	def connect(self):
		self.id = self.scope['user'].id
		logging.info(f"Player {self.id} wants to play a match!")
		if is_player_in_matchmaking_or_rematch_room_already(self.id) or get_player_state(self.id) == CustomUser.StateOptions.INGAME:
			self.close(reason="Player already has a match in progress.")
			return
		room = find_room_to_join()
		if not room:
			room = create_matchmaking_room()
		add_player_to_matchmaking_room(room, self.id, self.channel_name)
		self.room_group_name = room.room_id
		async_to_sync(self.channel_layer.group_add)(
			self.room_group_name, self.channel_name
		)
		self.accept()
		set_user_state_sync(self.scope['user'], CustomUser.StateOptions.INGAME)
		if all([room.player1, room.player2]):
			data = set_match_data(room.player1.id, room.player2.id)
			match_serializer = MatchSerializer(data=data)
			if match_serializer.is_valid():
				match_serializer.save()
				async_to_sync(self.channel_layer.group_send)(
					self.room_group_name, {"type": "matchmaking_message", "message": match_serializer.data['id']}
				)
				logging.info(f"Matchmaking rooms after connect:{matchmaking_rooms}")
		logging.info(f"Matchmaking rooms after connect:{matchmaking_rooms}")

	def disconnect(self, close_code):
		for room in matchmaking_rooms:
			if (room.player1 is not None and room.player1.channel_name == self.channel_name) or (room.player2 is not None and room.player2.channel_name == self.channel_name):
				self.channel_layer.group_discard(self.room_group_name, self.channel_name)
				if (room.player1 is not None) and (self.id == room.player1.id):
					room.player1 = None
				else:
					room.player2 = None
				if (room.player1 is None) and (room.player2 is None):
					matchmaking_rooms.remove(room)
				set_user_state_sync(self.scope['user'], CustomUser.StateOptions.IDLE)
				break
		logging.info(f"Matchmaking rooms after disconnect:{matchmaking_rooms}")
	
	def receive(self, text_data):
		text_data_json = json.loads(text_data)
		message = text_data_json["message"]
		logging.info(f"Message in receive: {message}")

		# Send message to room group
		async_to_sync(self.channel_layer.group_send)(
			self.room_group_name, {"type": "matchmaking_message", "message": message}
		)
	
	def matchmaking_message(self, event):
		message = event["message"]
		logging.info(f"Received group message: {message}")
		self.send(text_data=json.dumps({"message": message}))
		self.close() # closes the websocket once the match_id has been sent to both of the players

################################
# MATCHMAKING Rematch Consumer #
################################

class RematchConsumer(WebsocketConsumer):
	def connect(self):
		self.id = self.scope['user'].id
		prev_match_id = self.scope['url_route']['kwargs'].get('prev_match_id')
		prev_match = get_prev_match(prev_match_id)
		logging.info(f"Player {self.id} wants a rematch!")
		if (is_player_in_matchmaking_or_rematch_room_already(self.id) or get_player_state(self.id) == CustomUser.StateOptions.INGAME
	  		or prev_match is None or player_in_prev_match(prev_match, self.id) == False):
			self.close(reason="Player already has a match in progress.")
			return
		room = find_rematch_room_to_join(prev_match_id)
		if not room:
			room = create_rematch_room(prev_match_id)
		add_player_to_matchmaking_room(room, self.id, self.channel_name)
		self.room_group_name = room.room_id
		async_to_sync(self.channel_layer.group_add)(
			self.room_group_name, self.channel_name
		)
		self.accept()
		set_user_state_sync(self.scope['user'], CustomUser.StateOptions.INGAME)
		if all([room.player1, room.player2]):
			data = set_match_data(prev_match.player2.id, prev_match.player1.id)
			match_serializer = MatchSerializer(data=data)
			if match_serializer.is_valid():
				match_serializer.save()
				async_to_sync(self.channel_layer.group_send)(
					self.room_group_name, {"type": "matchmaking_message", "message": match_serializer.data['id']}
				)
				logging.info(f"Rematch matchmaking_rooms after connect: {rematch_rooms}")
		logging.info(f"Rematch matchmaking_rooms after connect: {rematch_rooms}")

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
				set_user_state_sync(self.scope['user'], CustomUser.StateOptions.IDLE)
				break
		logging.info(f"Rematch matchmaking_rooms after disconnect: {rematch_rooms}")
	
	def receive(self, text_data):
		text_data_json = json.loads(text_data)
		message = text_data_json["message"]
		logging.info(f"Message in receive: {message}")

		# Send message to room group
		async_to_sync(self.channel_layer.group_send)(
			self.room_group_name, {"type": "matchmaking_message", "message": message}
		)
	
	def matchmaking_message(self, event):
		message = event["message"]
		logging.info(f"Received group message: {message}")
		self.send(text_data=json.dumps({"message": message}))
		self.close() # closes the websocket once the match_id has been sent to both of the players

#################
# PONG Consumer #
#################
class PongConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.id = self.scope['user'].id
		match_id = self.scope['url_route']['kwargs'].get('match_id')
		logging.info(f"Player {self.id} is ready to play match {match_id}!")
		if is_player_in_pong_room_already(self.id) or await (get_match_status(match_id)) == Match.StatusOptions.FINISHED:
			logging.info(f"Player {self.id} in room already or connecting to a finished match")
			await self.close()
			return
		pong_room = find_pong_room_to_join(match_id)
		if not pong_room:
			pong_room = create_pong_room(match_id)
		try:
			await add_player_to_pong_room(match_id, pong_room, self.id, self.channel_name)
		except ValueError:
			logging.info("VALUE ERROR")
			await self.close()
			return
		await self.channel_layer.group_add(
			pong_room.match_group_name, 
			self.channel_name
		)
		await self.accept()
		await set_user_state(self.scope['user'], CustomUser.StateOptions.INGAME)
		logging.info("Rooms after connect:")
		logging.info(pong_rooms)
		async with pong_room.lock:
			if (pong_room.player1 is not None) and (pong_room.player2 is not None) and (pong_room.in_progress_flag == False):
				pong_room.in_progress_flag = True
				await self.play_pong(pong_room)
			elif pong_room.in_progress_flag == True:
				logging.info("The game is already in progress.")
			else:
				# only happens if the websockets connect one after another
				logging.info("Waiting for more players to join the match room.")
				match_database = await sync_to_async(get_object_or_404)(Match, id=pong_room.match_id)
				grace_period_dict[pong_room.match_id] = asyncio.create_task(self.grace_period_handler(pong_room, match_database))
				await set_match_status(match_database, Match.StatusOptions.INPROGRESS)
				await self.channel_layer.group_send(
					pong_room.match_group_name, {
						"type": "grace_disconnect",
						"message": "grace_disconnect",
					}
				)

	async def disconnect(self, close_code):
		logging.info(f"Disconnecting player {self.id} from pong")
		pong_room_grace = find_player_in_pong_room(self.id)
		if pong_room_grace is not None:
			match_database = await sync_to_async(get_object_or_404)(Match, id=pong_room_grace.match_id)
			match_winner = await get_match_winner(pong_room_grace.match_id)
			if (match_winner is None) and (pong_room_grace.match_id not in grace_period_dict):
				grace_period_dict[pong_room_grace.match_id] = asyncio.create_task(self.grace_period_handler(pong_room_grace, match_database))
				pong_room_grace.game_loop.cancel()
				pong_room_grace.in_progress_flag = False
				await self.channel_layer.group_send(
					pong_room_grace.match_group_name, {
						"type": "grace_disconnect",
						"message": "grace_disconnect",
					}
				)
			elif (match_winner is None):
				logging.info(f"Both players disconnected, setting winner to the one who disconnected last")
				grace_period_task = grace_period_dict[pong_room_grace.match_id]
				logging.info("Cancelling grace period from disconnect...")
				grace_period_task.cancel()
				grace_period_dict.pop(pong_room_grace.match_id)
				await set_match_winner_on_dc(match_database, pong_room_grace)
				#await set_match_to_tie(match_database)

		await set_user_state(self.scope['user'], CustomUser.StateOptions.IDLE)
		for pong_room in pong_rooms:
			if (pong_room.player1 is not None and pong_room.player1.channel_name == self.channel_name) or (pong_room.player2 is not None and pong_room.player2.channel_name == self.channel_name):
				await self.channel_layer.group_discard(
					pong_room.match_group_name, self.channel_name
				)
				if (pong_room.player1 is not None) and (self.id == pong_room.player1.id):
					pong_room.player1 = None
				elif (pong_room.player2 is not None) and (self.id == pong_room.player2.id):
					pong_room.player2 = None
				if (pong_room.player1 is None) and (pong_room.player2 is None):
					pong_rooms.remove(pong_room)
				break
		logging.info("Rooms after disconnect:")
		logging.info(pong_rooms)

	async def receive(self, text_data):
		text_data_json = json.loads(text_data)
		message_type = text_data_json["type"]

		if message_type == "paddle_movement":
			pong_room = find_player_in_pong_room(self.id)
			if not pong_room:
				return
			if pong_room.player1.id == self.id:
				paddle = "paddle1"
			elif pong_room.player2.id == self.id:
				paddle = "paddle2"
			direction = text_data_json["direction"]
			await self.move_paddle(pong_room, paddle, direction)
	
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

	async def grace_disconnect(self, event):
		await self.send(text_data=json.dumps(
			{
				"type": event["message"]
			}
		))

	async def match_start(self, event):
		logging.info("match_start called")
		pong_room = find_player_in_pong_room(self.id)
		if pong_room is not None:
			grace_period_task = grace_period_dict.get(pong_room.match_id)
		if grace_period_task is not None:
			logging.info("Cancelling grace period...")
			grace_period_task.cancel()
			grace_period_dict.pop(pong_room.match_id)
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
				"player2_score": event["player2_score"],
				"game_start" : event["game_start"]
			}
		))

	async def match_end(self, event):
		logging.info("match_end called")
		pong_room = find_player_in_pong_room(self.id)
		if pong_room is not None:
			grace_period_task = grace_period_dict.get(pong_room.match_id)
		if grace_period_task is not None:
			logging.info("Cancelling grace period...")
			grace_period_task.cancel()
			grace_period_dict.pop(pong_room.match_id)
		await self.send(text_data=json.dumps(
			{
				"type": event["message"],
				"winner_id" : event["winner_id"],
				"winner_username" : event["winner_username"]
			}
		))
		await self.close()

	async def move_paddle(self, pong_room, paddle, direction):
		paddle_speed = pong_room.PADDLE_SPEED
		if paddle == "paddle1":
			if direction == "UP" and pong_room.paddle1.position.y > (pong_room.GAME_HALF_HEIGHT - pong_room.paddle1.paddle_half_height) * (-1):
				pong_room.paddle1.position.y -= paddle_speed
			elif direction == "DOWN" and pong_room.paddle1.position.y < (pong_room.GAME_HALF_HEIGHT - pong_room.paddle1.paddle_half_height):
				pong_room.paddle1.position.y += paddle_speed
		elif paddle == "paddle2":
			if direction == "UP" and pong_room.paddle2.position.y > (pong_room.GAME_HALF_HEIGHT - pong_room.paddle2.paddle_half_height) * (-1):
				pong_room.paddle2.position.y -= paddle_speed
			elif direction == "DOWN" and pong_room.paddle2.position.y < (pong_room.GAME_HALF_HEIGHT - pong_room.paddle2.paddle_half_height):
				pong_room.paddle2.position.y += paddle_speed

	async def play_pong(self, pong_room):
		match_database = await sync_to_async(get_object_or_404)(Match, id=pong_room.match_id)
		await set_match_status(match_database, Match.StatusOptions.INPROGRESS)
		await asyncio.sleep(1)
		await self.channel_layer.group_send(
			pong_room.match_group_name, {
				"type": "match_start",
				"message": "match_start",
				"ball_x": pong_room.ball.position.x,
				"ball_y": pong_room.ball.position.y,
				"paddle1_x": pong_room.paddle1.position.x,
				"paddle1_y": pong_room.paddle1.position.y,
				"paddle2_x": pong_room.paddle2.position.x,
				"paddle2_y": pong_room.paddle2.position.y,
				"player1_score": pong_room.player1.score,
				"player2_score": pong_room.player2.score,
				"game_start" : pong_room.set_game_start_time(seconds_to_start=5).isoformat()
			}
		)
		# await asyncio.sleep(1)
		logging.info(f"Starting game for: ")
		logging.info(pong_room)
		pong_room.game_loop = asyncio.create_task(self.game_loop(pong_room, match_database))

	async def game_loop(self, pong_room, match_database):
		#await asyncio.sleep(3)
		try:
			logging.info(f"Game will start in: {pong_room.get_seconds_until_game_start()} seconds")
			await asyncio.sleep(pong_room.get_seconds_until_game_start())
			sequence = 0
			ball = pong_room.ball
			paddle1 = pong_room.paddle1
			paddle2 = pong_room.paddle2
			
			while 42:
				if pong_room.player1 is None or pong_room.player2 is None:
					break

				if ball.position.y > (pong_room.GAME_HALF_HEIGHT - (ball.size / 2)):
					if ball.direction.y > 0:
						ball.direction.y *= -1
				elif ball.position.y < ((pong_room.GAME_HALF_HEIGHT - (ball.size / 2))) * (-1):
					if ball.direction.y < 0:
						ball.direction.y *= -1

				# # Ball collision with floor & ceiling
				# if (ball.position.y > (pong_room.GAME_HALF_HEIGHT - (ball.size / 2))) or ((ball.position.y < ((pong_room.GAME_HALF_HEIGHT - (ball.size / 2))) * (-1))):
				# 	ball.direction.y *= -1

				# might be a source of bugs, watch out
				ball = paddle_collision(ball, paddle1, paddle2)
				ball_right = ball.position.x + (ball.size / 2)
				ball_left = ball.position.x - (ball.size / 2)

				# Scoring player 2 - ball out of bounds on the left side
				if (ball_left <= (0 - pong_room.GAME_HALF_WIDTH)):
					pong_room.player2.score += 1
					match_database.player2_score += 1
					await sync_to_async(match_database.save)(update_fields=["player2_score"])
					pong_room.reset()
					ball = pong_room.ball
					paddle1 = pong_room.paddle1
					paddle2 = pong_room.paddle2

				# Scoring player 1 - ball out of bounds on the right side
				if (ball_right >= (pong_room.GAME_HALF_WIDTH)):
					pong_room.player1.score += 1
					match_database.player1_score += 1
					await sync_to_async(match_database.save)(update_fields=["player1_score"])
					pong_room.reset()
					ball = pong_room.ball
					paddle1 = pong_room.paddle1
					paddle2 = pong_room.paddle2

				# Update ball position
				ball.position += ball.direction * ball.speed

				sequence += 1
				#logging.info(f"Sending draw message to player 1: {pong_room.player1.channel_name}")
				await self.channel_layer.send(
					pong_room.player1.channel_name, {
						"type": "draw",
						"message": "draw",
						"sequence": sequence,
						"for_player": pong_room.player1.id,
						"ball_x": ball.position.x,
						"ball_y": ball.position.y,
						"paddle1_x": paddle1.position.x,
						"paddle1_y": paddle1.position.y,
						"paddle2_x": paddle2.position.x,
						"paddle2_y": paddle2.position.y,
						"player1_score": pong_room.player1.score,
						"player2_score": pong_room.player2.score
					}
				)

				#logging.info(f"Sending draw message to player 2: {pong_room.player2.channel_name}")
				await self.channel_layer.send(
					pong_room.player2.channel_name, {
						"type": "draw",
						"message": "draw",
						"sequence": sequence,
						"for_player": pong_room.player1.id,
						"ball_x": ball.position.x,
						"ball_y": ball.position.y,
						"paddle1_x": paddle1.position.x,
						"paddle1_y": paddle1.position.y,
						"paddle2_x": paddle2.position.x,
						"paddle2_y": paddle2.position.y,
						"player1_score": pong_room.player1.score,
						"player2_score": pong_room.player2.score
					}
				)

				# Game over
				if match_database.player1_score >= GAME_CONSTANTS['MAX_SCORE'] or match_database.player2_score >= GAME_CONSTANTS['MAX_SCORE']:
					await set_match_winner(match_database)
					break

				# Short sleep
				await asyncio.sleep(0.01)
			if match_database.winner:
				logging.info(f"Match end for match {pong_room.match_id}")
				await self.channel_layer.group_send(
						pong_room.match_group_name, {
							"type" : "match_end",
							"message" : "match_end",
							"winner_id" : match_database.winner.id,
							"winner_username" : match_database.winner.username
						}
					)
		except asyncio.CancelledError:
			logging.info("Cancelled execution of game loop")
			pass
	async def grace_period_handler(self, pong_room, match):
		try:
			logging.info("Starting grace period...")
			await asyncio.sleep(30)
			await set_match_winner_on_dc(match, pong_room)
			logging.info(f"Match end (win by default) for match {pong_room.match_id}")
			await self.channel_layer.group_send(
					pong_room.match_group_name, {
						"type" : "match_end",
						"message" : "match_end",
						"winner_id" : match.winner.id,
						"winner_username" : match.winner.username
					}
				)
		except asyncio.CancelledError:
			pass