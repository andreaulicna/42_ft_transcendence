from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from rest_framework.authtoken.models import Token

class User(AbstractUser):
	ROLE_CHOICES = (
		('admin', 'Admin'),
		('player', 'Player')
	)
	role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='player')
