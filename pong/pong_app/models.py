from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from enum import Enum

class Player(AbstractBaseUser):
	id = models.AutoField(primary_key=True)
	username = models.CharField(max_length=20, blank=False, null=False, unique=False)

	def __str__(self):
		return f'Player: [ id: {self.id}, username: {self.username} ]'

class PlayerMatch(models.Model):
	id = models.AutoField(primary_key=True)
	match_id = models.ForeignKey('Match', on_delete=models.CASCADE, null=False, blank=False)
	player_id = models.ForeignKey(Player, on_delete=models.CASCADE, null=False, blank=False)
	score = models.IntegerField(default=0, null=False, blank=False)
	won = models.BooleanField(default=False, null=False, blank=False)

	def __str__(self):
		return f"Score: {self.score}"



class Match(models.Model):
	class State(Enum):
		PLAYED = "PLY"
		UNPLAYED = "UPL"

		@classmethod
		def choices(cls):
			return [(choice.value, choice.name) for choice in cls]

	id = models.AutoField(primary_key=True)
	round = models.IntegerField(default=1)
	state = models.CharField(max_length=3, choices=State.choices(), null=False, blank=False, default=State.UNPLAYED.value)