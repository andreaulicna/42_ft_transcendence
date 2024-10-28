from .models import CustomUser, Match, Friendship
from .serializers import UserSerializer, MatchSerializer, FriendshipSerializer
from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListCreateAPIView
from pathlib import Path
from django.core.files import File
import random
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework_simplejwt.tokens import RefreshToken
from django.middleware import csrf

class UserRegistrationView(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		serializer = UserSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class UserLoginView(ObtainAuthToken):
# 	def post(self, request, *args, **kwargs):
# 		username = request.data.get('username')
# 		password = request.data.get('password')
# 		user = authenticate(request, username=username, password=password)
# 		if user is not None:
# 			login(request, user)
# 			token, created = Token.objects.get_or_create(user=user)
# 			if created:
# 				token.delete()
# 				token = Token.objects.create(user=user)
# 			return Response({'token' : token.key, 'username' : user.username, 'role' : user.role})
# 		else:
# 			return Response({'detail' : 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

class UserInfoView(APIView):
		permission_classes = [IsAuthenticated]
		def get(self, request):
			try:
				player = CustomUser.objects.get(username=request.user)
			except CustomUser.DoesNotExist:
				return Response({'detail': 'Player does not exist'}, status=status.HTTP_404_NOT_FOUND)
			serializer = UserSerializer(player)
			return Response(serializer.data)
		def put(self, request):
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
		

# class UserLogoutView(APIView):
# 	permission_classes = [IsAuthenticated]

# 	def post(self, request):
# 		token_key = request.auth.key
# 		token = Token.objects.get(key=token_key)
# 		token.delete()
# 		return Response({'detail' : 'Successfully logged out.'})
	
class UserListView(ListCreateAPIView):
	queryset = CustomUser.objects.all()
	serializer_class = UserSerializer

class MatchView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		players = list(CustomUser.objects.all())
		if len(players) < 2:
			return Response({'detail': 'Waiting for more players.'}, status=status.HTTP_400_BAD_REQUEST) # will solve async eventually, now it just needs to return smt
		random_players = random.sample(players, 2)
		match_data = {
			'player1_id': random_players[0].id,
			'player2_id': random_players[1].id,
			'status': Match.StatusOptions.WAITING
		}
		match_serializer = MatchSerializer(data=match_data)
		if match_serializer.is_valid():
			match_serializer.save()
			return Response({'detail': 'Match successfully created.', 'match_id': match_serializer.data['id']}, status=status.HTTP_201_CREATED)
		else:
			return Response(match_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	
	def get(self, request):
		matches = Match.objects.filter(Q(player1_id=request.user.id) | Q(player2_id=request.user.id))
		if not matches:
			return Response({'detail':'No matches found'}, status=status.HTTP_404_NOT_FOUND)
		serializer = MatchSerializer(matches, many=True)
		return Response(serializer.data)
	
class FriendshipView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		players = list(CustomUser.objects.all())
		if len(players) < 2:
			return Response({'detail': 'Waiting for more players.'}, status=status.HTTP_400_BAD_REQUEST) # will solve async eventually, now it just needs to return smt
		try:
			players.pop(players.index(request.user))
		except ValueError:
			return Response({'detail': 'Existential crisis.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) # should never happen			
		random_friend = random.choice(players)
		sender_current = request.user
		receiver_current = random_friend
		print("Sender: ", sender_current.id, " Receiver: ", receiver_current.id)
		db_check = Friendship.objects.filter(Q(receiver_id=sender_current) | Q(sender_id=sender_current), Q(receiver_id=receiver_current) | Q(sender_id=receiver_current))
		if db_check:
			return Response({'detail': 'Friendship request ALREADY exists.'}, status=status.HTTP_200_OK)
		friendship_data = {
			'sender_id': sender_current.id,
			'receiver_id': receiver_current.id
		}
		friendship_serializer = FriendshipSerializer(data=friendship_data)
		if friendship_serializer.is_valid():
			friendship_serializer.save()
			return Response({'detail': 'Friendship request sent successfully.', 'friendship_id': friendship_serializer.data['id']}, status=status.HTTP_201_CREATED)
		else:
			return Response(friendship_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def get(self, request):
		friendships = Friendship.objects.filter(Q(sender_id=request.user.id) | Q(receiver_id=request.user.id))
	#	friendships = Friendship.objects.all()
		if not friendships:
			return Response({'detail':'You have no friends :('}, status=status.HTTP_404_NOT_FOUND)
		serializer = FriendshipSerializer(friendships, many=True)
		return Response(serializer.data)
	

class FriendshipDeleteView(APIView):
	permission_classes = [IsAuthenticated]

	def delete(self, request, pk):
		try:
			friendship_to_delete = get_object_or_404(Friendship, pk=pk)
			if ((friendship_to_delete.sender_id or friendship_to_delete.receiver_id) != request.user):
				raise Http404
			friendship_to_delete.delete()
			return Response({'detail': 'Friendship deleted successfully.'}, status=status.HTTP_200_OK)
		except Http404:
			return Response({'detail': 'Friendship not found.'}, status=status.HTTP_404_NOT_FOUND)
