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
from datetime import timedelta
from django.db import transaction
from django.core.files.base import ContentFile
from django.utils.translation import gettext as _



def get_tokens_for_user(user):
	refresh = RefreshToken.for_user(user)
		
	return {
		'refresh': str(refresh),
		'access': str(refresh.access_token),
	}

def set_response_cookie(response, data = None):
	if data is not None:
		expires = timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
		response.set_cookie(key = settings.SIMPLE_JWT['AUTH_COOKIE'], 
							value = data["refresh"],
							expires = expires,
							secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
							httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
							samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
							path = settings.SIMPLE_JWT['AUTH_COOKIE_PATH'])
	return response

def delete_auth_cookie(response):
	response.set_cookie(key = settings.SIMPLE_JWT['AUTH_COOKIE'], 
						value = '',
						expires = "Thu, 01 Jan 1970 00:00:00 GMT",
						secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
						httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
						samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
						path = settings.SIMPLE_JWT['AUTH_COOKIE_PATH'])
	
def delete_twofa_state_cookie(response):
	response.set_cookie(key = 'twofa_state',
						value = '',
						expires = "Thu, 01 Jan 1970 00:00:00 GMT",
						secure = True,
						httponly = True,
						samesite = 'Lax',
						path = reverse('login'))

def set_twofa_state_cookie(response, player_id):
	twofa_state_string = secrets.token_urlsafe(16)
	cache.set(twofa_state_string, player_id, 60)
	expires = timezone.now() + timedelta(seconds=60)
	response.set_cookie(key = 'twofa_state',
						value = twofa_state_string,
						expires = expires,
						secure = True,
						httponly = True,
						samesite = 'Lax',
						path = reverse('login'))
	return response

def two_factor_auth(user, data):
	otp_code = data.get('otp_code', None)
	if otp_code is None:
		return Response({"otp_required" : True, "details" : "OTP is yet to be provided"})
	totp = pyotp.TOTP(user.two_factor_secret)
	if not totp.verify(otp_code):
		return Response({'detail' : _('Invalid or expired OTP')}, status=status.HTTP_403_FORBIDDEN)

# optimize the call so that it only accesses the database once
def find_valid_random_username(current_username):
	rand_suffix = ''.join(random.choice(ascii_letters) for _ in range(4))
	suffixed_username = current_username + '_' + rand_suffix
	while CustomUser.objects.filter(username=suffixed_username).exists():
		rand_suffix = ''.join(random.choice(ascii_letters) for _ in range(4))
		suffixed_username = current_username + '_' + rand_suffix
	return suffixed_username

def csrf_failure(request, reason=""):
	return Response({'detail' : _('CSRF token missing')}, status=status.HTTP_403_FORBIDDEN)

class HealthCheckView(APIView):
	def get(self, request):
		return Response({'detail' : 'Healthy'})
	
class LoginView(APIView):
	permission_classes = []
	@method_decorator(csrf_exempt)
	def post(self, request, format=None):
		#logging.info(request.META)
		#logging.info(request.LANGUAGE_CODE)

		data = request.data
		response = Response()
		username = data.get('username', None)
		#twofa_state = data.get('twofa_state', None)
		password = data.get('password', None)
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				if user.two_factor:
					otp_code = data.get('otp_code', None)
					if otp_code is None:
						return Response({"otp_required" : True, "details" : _("OTP is yet to be provided")})
					totp = pyotp.TOTP(user.two_factor_secret)
					if not totp.verify(otp_code):
						return Response({'detail' : _('Invalid or expired OTP')}, status=status.HTTP_403_FORBIDDEN)
				data = get_tokens_for_user(user)
				response = set_response_cookie(response, data=data)
				csrf.get_token(request)
				response.data = {"access" : data['access']}
				return response
			else:
				return Response({"details" : _("This account is not active")},status=status.HTTP_404_NOT_FOUND)
		elif user is None and request.COOKIES.get('twofa_state') is not None:
			twofa_state_cookie = request.COOKIES.get('twofa_state')
			cached_twofa_state = cache.get(twofa_state_cookie, None)
			if cached_twofa_state is not None:
				try:
					user = CustomUser.objects.get(username=username)
					otp_code = data.get('otp_code', None)
					if otp_code is None:
						return Response({"otp_required" : True, "details" : _("OTP is yet to be provided")})
					totp = pyotp.TOTP(user.two_factor_secret)
					if not totp.verify(otp_code):
						return Response({'detail' : _('Invalid or expired OTP')}, status=status.HTTP_403_FORBIDDEN)
					if user.id == cached_twofa_state:
							cache.delete(cached_twofa_state)
							delete_twofa_state_cookie(response)
							data = get_tokens_for_user(user)
							response = set_response_cookie(response, data=data)
							csrf.get_token(request)
							response.data = {"access" : data['access']}
							#logging.info(response)
							return response
					else:
						return Response({'detail' : _('State not tied to user')}, status=status.HTTP_401_UNAUTHORIZED)
				except CustomUser.DoesNotExist:
					return Response({"details" : _("Invalid username provided")},status=status.HTTP_404_NOT_FOUND)
			else:
				return Response({'detail' : _('Request timed out, log in again')}, status=status.HTTP_403_FORBIDDEN)
		else:
			return Response({"details" : _("Invalid username or password")},status=status.HTTP_404_NOT_FOUND)

class RefreshView(TokenRefreshView):
	permission_classes = [AllowAny]
	serializer_class = CustomTokenRefreshSerializer
	@method_decorator(csrf_protect, name='refresh')
	def post (self, request):
		try:
			with transaction.atomic():
				serializer = self.serializer_class(data=request.data, context={'request': request})
				if serializer.is_valid():
					response = Response()
					data = serializer.validated_data
					response = set_response_cookie(response, data=data)
					response.data = {"access" : data['access']}

					return response
				return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		except TokenError as e:
			return Response({"details": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
		

class LogoutView(APIView):
	permission_classes = [IsAuthenticated]
	def post(self, request):
		player = CustomUser.objects.get(id=request.user.id)
		#logging.info(f"Player {player.id} is {player.state}")
		if player.state == CustomUser.StateOptions.INGAME:
			return Response({"details" : _("Logging out when in game is not possible")}, status=status.HTTP_403_FORBIDDEN)
		try:
			token = RefreshToken(request.COOKIES.get('refresh_token'))
			token.blacklist()
			response = Response({"detail": _("Successfully logged out")})
			delete_auth_cookie(response)
			#response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
			delete_twofa_state_cookie(response)
			#response.delete_cookie('twofa_state')
			return response
		except TokenError as e:
			return Response({"details" : _('Already logged out')},status=status.HTTP_401_UNAUTHORIZED)

#handle expiration of cached state
class IntraAuthorizationView(APIView):
	permission_classes = [AllowAny]
	def get(self, request):
		state = secrets.token_urlsafe(32)
		cache.set(state, "exists", 300)
		query_string = urlencode({"client_id" : f"{settings.INTRA_APP_UID}",
								"redirect_uri": f"{settings.PUBLIC_AUTH_URL}" + reverse('intra-callback'),
								"response_type" : "code",
								"state" : f"{state}"})
		authorization_url = "https://api.intra.42.fr/oauth/authorize?" + query_string
		#logging.info(f"Authorization URL: {authorization_url}")
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
			return Response({"details" : _("Invalid state parameter, try again")}, status=status.HTTP_403_FORBIDDEN)
		else:
			cache.delete(cached_state)

		code = request.query_params.get('code', None)
		error_msg = request.query_params.get('error', None)
		if error_msg is not None:
			return Response({"details" : error_msg}, status=status.HTTP_401_UNAUTHORIZED)
		if code is None:
			return Response({"details" : _("Code was not provided by 42 OAuth")}, status=status.HTTP_401_UNAUTHORIZED)

		token_request_data = {
			'grant_type' : 'authorization_code',
			'client_id' : settings.INTRA_APP_UID,
			'client_secret' : settings.INTRA_APP_SECRET,
			'code' : code,
			'redirect_uri' : f"{settings.PUBLIC_AUTH_URL}" + reverse('intra-callback')
		}
		token_response = requests.post("https://api.intra.42.fr/oauth/token", data=token_request_data)
		if not token_response.ok:
			return Response({"details" : _("Token was not provided by 42 OAuth")}, status=status.HTTP_401_UNAUTHORIZED)
		access_token = token_response.json().get('access_token', None)

		current_user_response = requests.get("https://api.intra.42.fr/v2/me",
			headers={"Authorization": f"Bearer {access_token}"})
		if not current_user_response.ok:
			return Response({"details" : _("Token provided by 42 OAuth is invalid or has expired")}, status=status.HTTP_401_UNAUTHORIZED)

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
			return Response({"details" : _("Intra account does not have a valid e-mail address associated with it")}, status=status.HTTP_404_NOT_FOUND)
		
		try:
			player = CustomUser.objects.get(email=email)
			existing_info = UserSerializer(player)
			#logging.info(f"Existing player info: {existing_info.data}")
			#logging.info(f"New info for existing: {player_info}")

			# Update the player's info
			for key, value in player_info.items():
				if value is not None and (getattr(player, key) is None or getattr(player, key) == ''):
					setattr(player, key, value)
			if not player.avatar:
				avatar_link = current_user_response.json().get('image')['link']
				avatar_response = requests.get(avatar_link)
				if avatar_response.ok:
					content_type = avatar_response.headers.get('Content-Type')
					if content_type:
						ext = content_type.split('/')[-1]
						player.avatar.save(f'avatar.{ext}', ContentFile(avatar_response.content))
			player.save()

			if player.two_factor:
				response = redirect(f"{settings.PUBLIC_AUTH_URL}" + '?username=' + player.username)
				response = set_twofa_state_cookie(response, player.id)
			else:
				data = get_tokens_for_user(player)
				response = redirect(f"{settings.PUBLIC_AUTH_URL}" + "?access_token=" + f"{data['access']}")
				response = set_response_cookie(response, data=data)
			csrf.get_token(request)
			return response

		except CustomUser.DoesNotExist:
			if CustomUser.objects.filter(username=player_info['username']).exists():
				player_info['username'] = find_valid_random_username(player_info['username'])
			player_info['password'] = make_password(None)

			player = UserSerializer(data=player_info)
			if player.is_valid():
				#logging.info(f"New player info: {player.validated_data}")
				player.save()
			else:
				return Response(player.errors, status=status.HTTP_400_BAD_REQUEST)
			
			player = CustomUser.objects.get(email=player_info['email'])
			if not player.avatar:
				avatar_link = current_user_response.json().get('image')['link']
				avatar_response = requests.get(avatar_link)
				if avatar_response.ok:
					content_type = avatar_response.headers.get('Content-Type')
					if content_type:
						ext = content_type.split('/')[-1]
						player.avatar.save(f'avatar.{ext}', ContentFile(avatar_response.content))
			player.save()
			
			data = get_tokens_for_user(player)
			response = redirect(f"{settings.PUBLIC_AUTH_URL}" + "?access_token=" + f"{data['access']}")
			response = set_response_cookie(response, data=data)
			csrf.get_token(request)
			return response


