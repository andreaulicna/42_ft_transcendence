from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from rest_framework.authtoken.models import Token
from django.utils.translation import gettext_lazy


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<username>/<filename>
    return "user_{0}/{1}".format(instance.username, filename)

class CustomUser(AbstractUser):
	class StateOptions(models.TextChoices):
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
