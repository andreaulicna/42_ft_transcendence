from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.middleware import csrf
from django.utils import timezone
from django.utils.http import urlencode
from rest_framework_simplejwt.views import TokenRefreshView
from .serializers import CustomTokenRefreshSerializer, UserSerializer
from rest_framework_simplejwt.exceptions import TokenError
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
import pyotp
import secrets
from django.core.cache import cache
import logging
from django.shortcuts import redirect
import requests
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from string import ascii_letters
import random

from django.http import HttpResponseRedirect

def get_tokens_for_user(user):
	refresh = RefreshToken.for_user(user)
		
	return {
		'refresh': str(refresh),
		'access': str(refresh.access_token),
	}

def set_response_cookie(request, player, is_redirect = False):
	data = get_tokens_for_user(player)
	expires = timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
	if is_redirect:
		response = redirect(f"{settings.PUBLIC_AUTH_URL}" + "?access_token=" + f"{data['access']}")
	else:
		response = Response()
	response.set_cookie(
						key = settings.SIMPLE_JWT['AUTH_COOKIE'], 
						value = data["refresh"],
						expires = expires,
						secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
						httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
						samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
						path = settings.SIMPLE_JWT['AUTH_COOKIE_PATH']
						)
	csrf.get_token(request)
	# response.data = {"refresh": data['refresh'], "access" : data['access']}
	return response

# optimize the call so that it only accesses the database once
def find_valid_random_username(current_username):
	rand_suffix = ''.join(random.choice(ascii_letters) for _ in range(4))
	suffixed_username = current_username + '_' + rand_suffix
	while CustomUser.objects.filter(username=suffixed_username).exists():
		rand_suffix = ''.join(random.choice(ascii_letters) for _ in range(4))
		suffixed_username = current_username + '_' + rand_suffix
	return suffixed_username

class HealthCheckView(APIView):
	def get(self, request):
		return Response({'detail' : 'Healthy'})

class LoginView(APIView):
	permission_classes = []
	@method_decorator(csrf_exempt)
	def post(self, request, format=None):
		data = request.data
		response = Response()
		username = data.get('username', None)
		password = data.get('password', None)
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				if user.two_factor:
					totp = pyotp.TOTP(user.two_factor_secret)
					otp_code = data.get('otp_code', None)
					if otp_code is None:
						return Response({"otp_required" : True, "details" : "OTP is yet to be provided"})
					if not totp.verify(otp_code):
						return Response({'detail' : 'Invalid or expired OTP'}, status=status.HTTP_403_FORBIDDEN)
				data = get_tokens_for_user(user)
				expires = timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
				response.set_cookie(
									key = settings.SIMPLE_JWT['AUTH_COOKIE'], 
									value = data["refresh"],
									expires = expires,
									secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
									httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
									samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
									path = settings.SIMPLE_JWT['AUTH_COOKIE_PATH']
										)
				csrf.get_token(request)
				response.data = {"refresh": data['refresh'], "access" : data['access']}
				return response
			else:
				return Response({"details" : "This account is not active"},status=status.HTTP_404_NOT_FOUND)
		else:
			return Response({"details" : "Invalid username or password"},status=status.HTTP_404_NOT_FOUND)

class RefreshView(TokenRefreshView):
	permission_classes = [AllowAny]
	serializer_class = CustomTokenRefreshSerializer
	@method_decorator(csrf_protect, name='refresh')
	def post (self, request):
		try:
			serializer = self.serializer_class(data=request.data, context={'request': request})
			response = Response()
			if serializer.is_valid():
				data = serializer.validated_data
				expires = timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
				response.set_cookie(
									key = settings.SIMPLE_JWT['AUTH_COOKIE'],
									value = data["refresh"],
									expires = expires,
									secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
									httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
									samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
									path = settings.SIMPLE_JWT['AUTH_COOKIE_PATH']
									)
				#csrf.get_token(request)
				response.data = data

				return response
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		except TokenError as e:
			return Response({"details" : str(e)},status=status.HTTP_401_UNAUTHORIZED)
		

class LogoutView(APIView):
	permission_classes = [IsAuthenticated]
	def post(self, request):
		player = CustomUser.objects.get(username=request.user)
		if player.state == CustomUser.StateOptions.INGAME:
			return Response({"details" : "Logging out when in game is not possible"}, status=status.HTTP_403_FORBIDDEN)
		try:
			token = RefreshToken(request.COOKIES.get('refresh_token'))
			token.blacklist()
			response = Response({"detail": "Successfully logged out"})
			response.set_cookie(
									key = settings.SIMPLE_JWT['AUTH_COOKIE'], 
									value = token,
									expires = timezone.now(),
									secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
									httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
									samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
									path = settings.SIMPLE_JWT['AUTH_COOKIE_PATH']
										)
			#player.status_counter = 0
			#player.save(update_fields=["status_counter"])
			return response
		except TokenError as e:
			return Response({"details" : str(e)},status=status.HTTP_401_UNAUTHORIZED)

#handle expiration of cached state
class IntraAuthorizationView(APIView):
	permission_classes = [AllowAny]
	def get(self, request):
		state = secrets.token_urlsafe(32)
		cache.set(state, "exists", 600)
		query_string = urlencode({"client_id" : f"{settings.INTRA_APP_UID}",
								"redirect_uri": f"{settings.PUBLIC_AUTH_URL}" + reverse('intra-callback'),
								"response_type" : "code",
								"state" : f"{state}"})
		authorization_url = "https://api.intra.42.fr/oauth/authorize?" + query_string
		logging.info(f"Authorization URL: {authorization_url}")
		return Response({"URL": authorization_url})
	
# What if they are already authenticated?
# handle 2FA?
# redirect on failure instead of 4xx?
# resolve avatar issues
class IntraCallbackView(APIView):
	permission_classes = [AllowAny]

	def get(self, request):

		returned_state = request.query_params.get('state', None)
		cached_state = cache.get(returned_state, None)
		if cached_state == None:
			return Response({"details" : "Invalid state parameter, try again"}, status=status.HTTP_403_FORBIDDEN)
		else:
			cache.delete(cached_state)

		code = request.query_params.get('code', None)
		error_msg = request.query_params.get('error', None)
		if error_msg is not None:
			return Response({"details" : error_msg}, status=status.HTTP_401_UNAUTHORIZED)
		if code is None:
			return Response({"details" : "Code was not provided by 42 OAuth"}, status=status.HTTP_401_UNAUTHORIZED)

		token_request_data = {
			'grant_type' : 'authorization_code',
			'client_id' : settings.INTRA_APP_UID,
			'client_secret' : settings.INTRA_APP_SECRET,
			'code' : code,
			'redirect_uri' : f"{settings.PUBLIC_AUTH_URL}" + reverse('intra-callback')
		}
		token_response = requests.post("https://api.intra.42.fr/oauth/token", data=token_request_data)
		if not token_response.ok:
			return Response({"details" : "Token was not provided by 42 OAuth"}, status=status.HTTP_401_UNAUTHORIZED)
		access_token = token_response.json().get('access_token', None)

		current_user_response = requests.get("https://api.intra.42.fr/v2/me",
			headers={"Authorization": f"Bearer {access_token}"})
		if not current_user_response.ok:
			return Response({"details" : "Token provided by 42 OAuth is invalid or has expired"}, status=status.HTTP_401_UNAUTHORIZED)
		
		# needs protection if image is empty
		player_info =  {
			"email": current_user_response.json().get('email'),
			"username": current_user_response.json().get('login'),
			"first_name": current_user_response.json().get('first_name'),
			"last_name": current_user_response.json().get('last_name'),
			#"avatar": current_user_response.json()['image']['link']
   		}
		email = player_info['email']
		if email == None:
			return Response({"details" : "Intra account does not have a valid e-mail address associated with it"}, status=status.HTTP_404_NOT_FOUND)
		
		try:
			player = CustomUser.objects.get(email=email)
			existing_info = UserSerializer(player)
			logging.info(f"Existing player info: {existing_info.data}")
			logging.info(f"New info for existing: {player_info}")

			# Update the player's info
			for key, value in player_info.items():
				if value is not None and (getattr(player, key) is None or getattr(player, key) is ''):
					setattr(player, key, value)
			player.save()

			# updated_info = UserSerializer(player)
			# logging.info(f"Existing player info after update: {updated_info.data}")

			response = set_response_cookie(request, player, is_redirect=True)
			return response

		except CustomUser.DoesNotExist:
			if CustomUser.objects.filter(username=player_info['username']).exists():
				player_info['username'] = find_valid_random_username(player_info['username'])
			player_info['password'] = make_password(None)

			player = UserSerializer(data=player_info)
			if player.is_valid():
				logging.info(f"New player info: {player.validated_data}")
				player.save()
			else:
				return Response(player.errors, status=status.HTTP_400_BAD_REQUEST)
			
			player = CustomUser.objects.get(email=player_info['email'])
			response = set_response_cookie(request, player, is_redirect=True)
			return response


