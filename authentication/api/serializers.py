from rest_framework_simplejwt.serializers import TokenRefreshSerializer 
from rest_framework_simplejwt.exceptions import InvalidToken
from django.conf import settings
from .models import CustomUser
from rest_framework import serializers



class CustomTokenRefreshSerializer(TokenRefreshSerializer):
	refresh = None
	def validate(self, attrs):
		refresh_token = settings.SIMPLE_JWT['AUTH_COOKIE']
		print(self.context)
		attrs['refresh'] = self.context['request'].COOKIES.get(refresh_token)
		if attrs['refresh']:
			return super().validate(attrs)
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