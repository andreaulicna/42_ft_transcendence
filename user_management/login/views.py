from django.shortcuts import render
from .models import CustomUser
from .serializers import UserSerializer
from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from pathlib import Path
from django.core.files import File

class UserRegistrationView(APIView):
	def post(self, request):
		serializer = UserSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(ObtainAuthToken):
	def post(self, request, *args, **kwargs):
		username = request.data.get('username')
		password = request.data.get('password')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			token, created = Token.objects.get_or_create(user=user)
			if created:
				token.delete()
				token = Token.objects.create(user=user)
			return Response({'token' : token.key, 'username' : user.username, 'role' : user.role})
		else:
			return Response({'detail' : 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

class UserInfoView(APIView):
		permission_classes = [IsAuthenticated]
		def get(self, request):
			try:
				player = CustomUser.objects.get(username=request.user)
			except CustomUser.DoesNotExist:
				return Response({'detail': 'Player does not exist'}, status=status.HTTP_404_NOT_FOUND)
			serializer = UserSerializer(player)
			return Response(serializer.data)
		def post(self, request):
			try:
				player = CustomUser.objects.get(username=request.user)
			except CustomUser.DoesNotExist:
				return Response({'detail': 'Player does not exist'}, status=status.HTTP_404_NOT_FOUND)
			first_name = request.data.get('first_name')
			last_name = request.data.get('last_name')
			if first_name:
				new_first_name = ' '.join(first_name.split())
				player.first_name = new_first_name
			if last_name:
				new_last_name = ' '.join(last_name.split())
				player.last_name = new_last_name
			player.save()
			return Response({'detail' : 'User info updated'})


# protect against identical names and big amounts
class UserAvatarUpload(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		try:
			player = CustomUser.objects.get(username=request.user)
		except CustomUser.DoesNotExist:
			return Response({'detail': 'Player does not exist'}, status=status.HTTP_404_NOT_FOUND)

		# Specify the local file path
		local_file_path = '/app/test_media/emoji_template.jpg'
		
		# Open the local file
		with open(local_file_path, 'rb') as f:
			# Save the file to the user's ImageField
			player.avatar.save(Path(local_file_path).name, File(f))
		
		player.save()
		return Response({'detail': 'Avatar updated successfully'})
	
	def get(self, request):
		try:
			player = CustomUser.objects.get(username=request.user)
		except CustomUser.DoesNotExist:
			return Response({'detail': 'Player does not exist'}, status=status.HTTP_404_NOT_FOUND)
		serializer = UserSerializer(player)
		return Response({'avatar' : serializer.data['avatar']})
		

class UserLogoutView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		token_key = request.auth.key
		token = Token.objects.get(key=token_key)
		token.delete()
		return Response({'detail' : 'Successfully logged out.'})