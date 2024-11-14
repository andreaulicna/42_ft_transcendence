from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from rest_framework.authtoken.models import Token
from django.utils.translation import gettext_lazy
import uuid


def user_directory_path(instance, filename):
	# file will be uploaded to MEDIA_ROOT/user_<username>/<filename>
	return "user_{0}/{1}".format(instance.username, filename)

'''
Default fields:
id
last_login (NULL)
is_superuser (false)
username
first_name (NULL)
last_name (NULL)
is_staff (false)
is_active (true)
date_joined
groups[] (NULL)
user_permissions[] (NULL)
'''
class CustomUser(AbstractUser):
	class Meta:
		managed = False
	class StateOptions(models.TextChoices):
		# [VALUE IN CODE] = [DB NAME], [human readable name]
		OFFLINE = "OFF", gettext_lazy("Offline")
		ONLINE = "ON", gettext_lazy("Online")
		INGAME = "IG", gettext_lazy("In game")
		INTOURNAMENT = "IT", gettext_lazy("In tournament")

	ROLE_CHOICES = (
		('admin', 'Admin'),
		('player', 'Player')
	)
	role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='player')
	email = models.EmailField(unique=True)
	win_count = models.PositiveIntegerField(blank=False, default=0)
	loss_count = models.PositiveIntegerField(blank=False, default=0)
	state = models.CharField(max_length=3, choices=StateOptions, default=StateOptions.OFFLINE)
	avatar = models.ImageField(upload_to=user_directory_path, blank=True)
	two_factor = models.BooleanField(blank=False, default=False)

class Tournament(models.Model):
	class Meta:
		managed = False
	class StatusOptions(models.TextChoices):
		WAITING = "WAIT", gettext_lazy("Waiting")
		INPROGRESS = "IP", gettext_lazy("In progress")
		FINISHED = "FIN", gettext_lazy("Finished")

	class RoundOptions(models.TextChoices):
		QUARTER = "QR", gettext_lazy("Quarter-final")
		SEMI = "SEMI", gettext_lazy("Semi-final")
		FINAL = "FIN", gettext_lazy ("Final")

	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=30, default="unnamed")
	time_created = models.DateTimeField(auto_now_add=True)
	creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name="creator", null=True)
	status = models.CharField(max_length=4, choices=StatusOptions, default=StatusOptions.WAITING)
	winner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name="winner_tpurnament", null=True)

class Match(models.Model):
	class Meta:
		managed = False
	class StatusOptions(models.TextChoices):
		WAITING = "WAIT", gettext_lazy("Waiting")
		INPROGRESS = "IP", gettext_lazy("In progress")
		FINISHED = "FIN", gettext_lazy("Finished")

	id = models.AutoField(primary_key=True)
	time_created = models.DateTimeField(auto_now_add=True)
	status = models.CharField(max_length=4, choices=StatusOptions, default=StatusOptions.WAITING)
	player1 = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name="player1", null=True)
	player2 = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name="player2", null=True)
	player1_score = models.PositiveIntegerField(blank=False, default=0)
	player2_score = models.PositiveIntegerField(blank=False, default=0)
	winner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name="winner_match", null=True)
	tournament = models.ForeignKey(Tournament, on_delete=models.SET_NULL, null=True)
	round_number = models.PositiveIntegerField(blank=False, default=0)
	
class Friendship(models.Model):
	class Meta:
		managed = False
	class StatusOptions(models.TextChoices):
		PENDING = "PEN", gettext_lazy("Pending")
		ACCEPTED = "ACC", gettext_lazy("Accepted")

	id = models.AutoField(primary_key=True)
	status = models.CharField(max_length=3, choices=StatusOptions, default=StatusOptions.PENDING)
	sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sender")
	receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="receiver")

class PlayerTournament(models.Model):
	class Meta:
		managed = False
	id = models.AutoField(primary_key=True)
	player = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
	tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
	player_tmp_username = models.CharField(max_length=150, blank=True)

	def save(self, *args, **kwargs):
		if not self.player_tmp_username:
			self.player_tmp_username = self.player.username
		super().save(*args, **kwargs)

class WebSocketTicket(models.Model):
	class Meta:
		managed = False
	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
	uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)
	expires_at = models.DateTimeField()