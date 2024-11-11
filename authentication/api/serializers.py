from rest_framework_simplejwt.serializers import TokenRefreshSerializer 
from rest_framework_simplejwt.exceptions import InvalidToken
from django.conf import settings

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