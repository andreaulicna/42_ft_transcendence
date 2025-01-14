from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from rest_framework.authtoken.models import Token
from django.utils.translation import gettext_lazy
import uuid
from django.conf import settings
from django.contrib.postgres.fields import ArrayField


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
	class StateOptions(models.TextChoices):
		# [VALUE IN CODE] = [DB NAME], [human readable name]
		IDLE = "ID", gettext_lazy("Idle")
		INGAME = "IG", gettext_lazy("In game")

	ROLE_CHOICES = (
		('admin', 'Admin'),
		('player', 'Player')
	)
	role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='player')
	email = models.EmailField(unique=True)
	win_count = models.PositiveIntegerField(blank=False, default=0)
	loss_count = models.PositiveIntegerField(blank=False, default=0)
	state = models.CharField(max_length=3, choices=StateOptions, default=StateOptions.IDLE)
	status_counter = models.PositiveIntegerField(blank=False, default=0)
	avatar = models.ImageField(upload_to=user_directory_path, blank=True)
	two_factor = models.BooleanField(blank=False, default=False)
	two_factor_secret = models.CharField(max_length=32, blank=True, null=True)

class AbstractTournament(models.Model):
	class Meta:
		abstract = True

	class StatusOptions(models.TextChoices):
		WAITING = "WAIT", gettext_lazy("Waiting")
		INPROGRESS = "IP", gettext_lazy("In progress")
		FINISHED = "FIN", gettext_lazy("Finished")

	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=30, default="unnamed")
	time_created = models.DateTimeField(auto_now_add=True)
	creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name="%(class)s_creator", null=True)
	status = models.CharField(max_length=4, choices=StatusOptions, default=StatusOptions.WAITING)
	capacity = models.PositiveIntegerField(blank=False, default=0)

class Tournament(AbstractTournament):

	winner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name="winner_tpurnament", null=True)

class LocalTournament(AbstractTournament):

	winner = models.CharField(max_length=150, blank=True)
	players = ArrayField(models.CharField(max_length=150), blank=True, default=list)

class AbstractMatch(models.Model):
	class Meta:
		abstract = True
	
	class StatusOptions(models.TextChoices):
		WAITING = "WAIT", gettext_lazy("Waiting")
		INPROGRESS = "IP", gettext_lazy("In progress")
		FINISHED = "FIN", gettext_lazy("Finished")

	id = models.AutoField(primary_key=True)
	time_created = models.DateTimeField(auto_now_add=True)
	status = models.CharField(max_length=4, choices=StatusOptions, default=StatusOptions.WAITING)
	player1_score = models.PositiveIntegerField(blank=False, default=0)
	player2_score = models.PositiveIntegerField(blank=False, default=0)
	default_ball_size = models.FloatField(blank=False, default=0)
	default_paddle_height = models.FloatField(blank=False, default=0)
	default_paddle_width = models.FloatField(blank=False, default=0)
	default_paddle_speed = models.FloatField(blank=False, default=0)
	tournament = models.ForeignKey(Tournament, on_delete=models.SET_NULL, null=True)
	round_number = models.PositiveIntegerField(blank=False, default=0)

class Match(AbstractMatch):

	player1 = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name="player1", null=True)
	player2 = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name="player2", null=True)
	winner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name="winner_match", null=True)

class LocalMatch(AbstractMatch):

	creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name="local_creator", null=True)
	player1_tmp_username = models.CharField(max_length=150, blank=True)
	player2_tmp_username = models.CharField(max_length=150, blank=True)
	winner = models.CharField(max_length=150, blank=True)

class AIMatch(AbstractMatch):

	creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name="ai_creator", null=True)
	winner = models.CharField(max_length=150, blank=True)

class Friendship(models.Model):
	class StatusOptions(models.TextChoices):
		PENDING = "PEN", gettext_lazy("Pending")
		ACCEPTED = "ACC", gettext_lazy("Accepted")

	id = models.AutoField(primary_key=True)
	status = models.CharField(max_length=3, choices=StatusOptions, default=StatusOptions.PENDING)
	sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sender")
	receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="receiver")

class PlayerTournament(models.Model):
	id = models.AutoField(primary_key=True)
	player = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
	tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
	player_tmp_username = models.CharField(max_length=150, blank=True)

	def save(self, *args, **kwargs):
		if not self.player_tmp_username:
			self.player_tmp_username = self.player.username
		super().save(*args, **kwargs)
