from rest_framework_simplejwt.serializers import TokenRefreshSerializer 

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
	def validate(self, attrs):
		data = super(CustomTokenRefreshSerializer, self).validate(attrs)
		return data