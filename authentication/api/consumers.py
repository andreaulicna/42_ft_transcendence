from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import CustomUser, Match
import logging
from django.db.models import F, Case, When, Value, PositiveIntegerField
import json
from django.db import models
from django.utils.translation import gettext_lazy
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
import uuid # unique online_room id
import asyncio
from django.db.models import Q

class OnlineRoom():
	def __init__(self):
		self.group_name = str(uuid.uuid4())
		self.players = []
	
	def __str__(self):
		return f"OnlineRoom(players={[str(player) for player in self.players]})"

online_room = OnlineRoom()

class OnlinePlayer:
	def __init__(self, player_id, player_channel_name, username):
		self.id = player_id
		self.channel_name = player_channel_name
		self.username = username

	def __str__(self):
		return f"OnlinePlayer(id={self.id}, channel_name={self.channel_name}, username={self.username})"


#{
# 'type': 'websocket', 
# 'path': '/api/auth/ws/login/consume/', 
# 'raw_path': b'/api/auth/ws/login/consume/', 
# 'root_path': '', 
# 'headers': [(b'upgrade', b'websocket'), (b'connection', b'upgrade'), (b'x-forwarded-for', b'192.168.65.1'), (b'host', b'localhost:4200'), (b'sec-websocket-version', b'13'), (b'sec-websocket-key', b'oz8cxW2v8gTJHQqN6Nh6Mg=='), (b'sec-websocket-extensions', b'permessage-deflate; client_max_window_bits')], 
# 'query_string': b'uuid=6145c83c-d2ce-49e8-934b-1b83a26c65ca', 
# 'client': ['172.18.0.7', 34330], 
# 'server': ['172.18.0.3', 9000], 
# 'subprotocols': [], 
# 'asgi': {'version': '3.0'}, 
# 'user': <CustomUser: testusr2>, 
# 'cookies': {}, 
# 'session': <django.utils.functional.LazyObject object at 0xffff96d59270>, 
# 'path_remaining': '', 
# 'url_route': {'args': (), 'kwargs': {}}}

# {'groups': [], 
# 'scope': ...
# 'channel_layer': None, 
# 'base_send': <bound method InstanceSessionWrapper.send of <channels.sessions.InstanceSessionWrapper object at 0xffffb8c2bd30>>, 
# 'id': 1}

@database_sync_to_async
def set_user_state(user, userState):
	user.state = userState
	user.save(update_fields=["state"])

@database_sync_to_async
def increment_user_status_counter(user):
	user.status_counter = F('status_counter') + 1
	user.save(update_fields=["status_counter"])

@database_sync_to_async
def decrement_user_status_counter(user):
	#user.refresh_from_db(fields=["status_counter"])
	user.status_counter = Case(
		When(status_counter__gt=0, then=F('status_counter') - 1),
		default=F('status_counter'),
		output_field=PositiveIntegerField()
	)
	user.save(update_fields=["status_counter"])

@database_sync_to_async
def add_player_to_online_room(player_id, player_channel_name):
	player_database = get_object_or_404(CustomUser, id=player_id)
	online_player = OnlinePlayer(player_id, player_channel_name, player_database.username)
	online_room.players.append(online_player)
	return online_player

@database_sync_to_async
def is_status_counter_zero(player_id):
	player_database = get_object_or_404(CustomUser, id=player_id)
	if (player_database.status_counter <= 0):
		return True
	return False

@database_sync_to_async
def get_inprogress_match(player_id):
	try:
		match_database = Match.objects.get(
			(Q(player1=player_id) | Q(player2=player_id)) & Q(status=Match.StatusOptions.INPROGRESS)
		)
		player = CustomUser.objects.get(id=player_id)
		if player.state == CustomUser.StateOptions.INGAME:
			return None
		return match_database.id
	except Match.DoesNotExist:
		return None
	except Match.MultipleObjectsReturned:
		logging.error("Multiple in-progress matches found for player.")
		return None


class UserConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.id = self.scope['user'].id
		#logging.info(f"Player {self.id} says hello from authentication!")
		player = await add_player_to_online_room(self.id, self.channel_name)
		await self.channel_layer.group_add(
			online_room.group_name, self.channel_name
		)
		if await is_status_counter_zero(self.id):
			await self.channel_layer.group_send(
				online_room.group_name,
				{
					"type": "user_status",
					"id": self.id,
					"username": player.username,
					"status": "ON"
				}
			)
		await increment_user_status_counter(self.scope['user'])
		await self.accept()
		logging.info("Online room after connect:")
		logging.info(online_room)
		self.timeout_task = asyncio.create_task(self.timeout_handler())
		inprogress_match_id = await get_inprogress_match(self.id)
		#logging.info(f"Found inprogress match: {inprogress_match_id}")
		if inprogress_match_id is not None:
			#logging.info("Sending match_id...")
			await self.send(text_data=json.dumps(
				{
					"type": "in_game",
					"match_id": inprogress_match_id
				}
			))

	async def disconnect(self, close_code):
		await decrement_user_status_counter(self.scope['user'])
		for player in online_room.players:
			if self.channel_name == player.channel_name:
				await self.channel_layer.group_discard(
					online_room.group_name, self.channel_name
				)
				if await is_status_counter_zero(self.id):
					await self.channel_layer.group_send(
						online_room.group_name,
						{
							"type": "user_status",
							"id": self.id,
							"username": player.username,
							"status": "OFF"
						}
					)
				online_room.players.remove(player)
				break

		logging.info("Online room after disconnect:")
		logging.info(online_room)
	
	async def receive(self, text_data):
		try:
			text_data_json = json.loads(text_data)
		except json.JSONDecodeError:
			# Handle the case where the JSON is invalid
			self.send(text_data=json.dumps({
				"error": "Invalid JSON format."
			}))
			return

		if text_data_json == "refresh":
			self.timeout_task.cancel()
			self.timeout_task = asyncio.create_task(self.timeout_handler())

	async def timeout_handler(self):
		try:
			await asyncio.sleep(3600)
			await self.close()
		except asyncio.CancelledError:
			pass
	
	async def user_status(self, event):
		message = {
			"type": "user_status",
			"id": event["id"],
			"username": event["username"],
			"status": event["status"]
		}
		await self.send(text_data=json.dumps(message))