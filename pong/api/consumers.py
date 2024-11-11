from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import CustomUser, Match
from pprint import pprint # nice printing
import json
from django.shortcuts import get_object_or_404
import random
from asgiref.sync import sync_to_async

match_rooms = []

def create_match_room(match_id):
	match_room = {
		'players': [],
		'match_id': match_id,
	}
	match_rooms.append(match_room)
	return match_room

def is_player_in_match_room_already(player_id):
	for math_room in match_rooms:
		for player in math_room['players']:
			if player_id in player:
				return True
	return False

def find_match_room_to_join(match_id):
	for match_room in match_rooms:
		if match_room['match_id'] == match_id and len(match_room['players']) < 2:
			return match_room
	return None

@database_sync_to_async
def add_player_to_room(match_id, match_room, player_id, channel_name):
	match_database = get_object_or_404(Match, id=match_id)
	if match_database.player2_id == player_id:
		match_room['players'].append({player_id: channel_name})
	else:
		match_room['players'].insert(0, {player_id: channel_name})

def get_player_id(match_id, player_index):
	for match_room in match_rooms:
		if match_room['match_id'] == match_id:
			return list(match_rooms['players'][player_index].keys()[0])

@database_sync_to_async
def set_user_state(user, userState):
	user.state = userState
	user.save(update_fields=["state"])

@database_sync_to_async
def set_match_status(match, matchStatus):
	match.status = matchStatus
	match.save(update_fields=['status'])

class PongConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.id = self.scope['user'].id
		match_id = self.scope['url_route']['kwargs'].get('match_id')
		print(f"Player {self.id} is ready to play match {match_id}!")
		await set_user_state(self.scope['user'], CustomUser.StateOptions.INGAME)
		if is_player_in_match_room_already(self.id):
			return
		match_room = find_match_room_to_join(match_id)
		if not match_room:
			match_room = create_match_room(match_id)
		await add_player_to_room(match_id, match_room, self.id, self.channel_name)
		self.match_group_name = match_room['match_id']
		await self.channel_layer.group_add(
			self.match_group_name, 
			self.channel_name
		)
		await self.accept()
		print("Rooms after connect:")
		pprint(match_rooms)
		if len(match_room['players']) == 2:
			await self.play_pong(match_room)
		else:
			print("Waiting for more players to join the match room.")

	async def disconnect(self, close_code):
		await set_user_state(self.scope['user'], CustomUser.StateOptions.ONLINE)
		for match_room in match_rooms:
			for player in match_room['players']:
				if self.channel_name in player.values():
					await self.channel_layer.group_discard(
						self.match_group_name, self.channel_name
					)
					match_room['players'].remove(player)
					if not match_room['players']:
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
		match_database = await sync_to_async(get_object_or_404)(Match, id=match_room['match_id'])
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
			match_database = await sync_to_async(get_object_or_404)(Match, id=match_room['match_id'])
			if match_database.player1_score > match_database.player2_score:
				highest_score = match_database.player1_score
			else:
				highest_score = match_database.player2_score
		await set_match_status(match_database, Match.StatusOptions.FINISHED)
			
