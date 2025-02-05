from rest_framework_simplejwt.serializers import TokenRefreshSerializer 
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from django.conf import settings
from .models import CustomUser
from rest_framework import serializers
from datetime import datetime

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
	token_class = RefreshToken
	refresh = None
	def validate(self, attrs):
		refresh_token = settings.SIMPLE_JWT['AUTH_COOKIE']
		attrs['refresh'] = self.context['request'].COOKIES.get(refresh_token)
		if attrs['refresh']:
			refresh = self.token_class(attrs["refresh"])
			data = {"access": str(refresh.access_token)}
			if api_settings.ROTATE_REFRESH_TOKENS:
				if api_settings.BLACKLIST_AFTER_ROTATION:
					try:
						# Attempt to blacklist the given refresh token
						refresh.blacklist()
					except AttributeError:
						# If blacklist app not installed, `blacklist` method will
						# not be present
						pass
				refresh.set_jti()
				refresh.set_exp()
				refresh.set_iat()

				data["refresh"] = str(refresh)
				auth = JWTAuthentication()
				user = auth.get_user(validated_token=refresh)
				OutstandingToken.objects.create(
					user=user,
					jti=refresh[api_settings.JTI_CLAIM],
					token=data["refresh"],
					created_at=datetime.fromtimestamp(refresh["iat"]),
					expires_at=datetime.fromtimestamp(refresh["exp"]),
				)

			return data
		else:
			raise InvalidToken(f'No valid token found in cookie {refresh_token}')
		
class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = '__all__' # returns all parameters
		extra_kwargs = {'password' : {'write_only': True}, 
						'two_factor_secret' : {'write_only' : True}} # protects GET user/info/ from exposing the hash of the password in the response

	def create(self, validated_data):
		user = CustomUser.objects.create_user(**validated_data)
		return user