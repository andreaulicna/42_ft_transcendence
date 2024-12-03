from .models import CustomUser, Match, Friendship
from .serializers import UserSerializer, MatchSerializer, FriendshipSerializer, FriendshipListSerializer, MatchStartSerializer, OtherUserSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListAPIView
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import Http404
import base64, os
from django.core.files.base import ContentFile

class UserRegistrationView(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		serializer = UserSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
			user_state = request.data.get('state')
			if first_name:
				new_first_name = ' '.join(first_name.split())
				player.first_name = new_first_name
			if last_name:
				new_last_name = ' '.join(last_name.split())
				player.last_name = new_last_name
			player.save()
			return Response({'detail' : 'User info updated'})
		
class UserInfoReset(APIView):
	permission_classes = [IsAuthenticated]
	def post(self, request):
		try:
			player = CustomUser.objects.get(username=request.user)
		except CustomUser.DoesNotExist:
			return Response({'detail': 'Player does not exist'}, status=status.HTTP_404_NOT_FOUND)
		player.state = CustomUser.StateOptions.IDLE
		player.status_counter = 0
		player.save()
		return Response({'detail' : 'User info reset to default'})
	
class OtherUserInfoView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request, pk):
		try:
			other_user = get_object_or_404(CustomUser, pk=pk)
			other_user_serializer = OtherUserSerializer(other_user)
			return Response(other_user_serializer.data)
		except Http404:
			return Response({'detail' : 'Other user not found'}, status=status.HTTP_404_NOT_FOUND)

# protect against identical names and big amounts
class UserAvatarUpload(APIView):
	permission_classes = [IsAuthenticated]

	def put(self, request):
		try:
			player = CustomUser.objects.get(username=request.user)
		except CustomUser.DoesNotExist:
			return Response({'detail': 'Player does not exist'}, status=status.HTTP_404_NOT_FOUND)
		# print(request.data)
		data = request.data['profilePic']
		if not data:
			return Response({'detail': 'No avatar data provided'}, status=status.HTTP_400_BAD_REQUEST)
		try:
			format, imgstr = data.split(';base64,')
			ext = format.split('/')[-1] 
			avatar_data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
			# Define the folder where the avatar is stored
			avatar_folder = os.path.dirname(player.avatar.path)

			# Delete existing files in the folder
			for filename in os.listdir(avatar_folder):
				file_path = os.path.join(avatar_folder, filename)
				if os.path.isfile(file_path):
					os.remove(file_path)
			
			# Save the file to the user's ImageField
			player.avatar.save(f'avatar.{ext}', avatar_data)
			player.save()
			return Response({'detail': 'Avatar updated successfully'})
		except Exception as e:
			return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
	
	def get(self, request):
		try:
			player = CustomUser.objects.get(username=request.user)
		except CustomUser.DoesNotExist:
			return Response({'detail': 'Player does not exist'}, status=status.HTTP_404_NOT_FOUND)
		serializer = UserSerializer(player)
		return Response({'avatar' : serializer.data['avatar']})
		
class UserListView(ListAPIView):
	queryset = CustomUser.objects.all().order_by('id')
	serializer_class = UserSerializer
	permission_classes = [IsAuthenticated]

class MatchView(ListAPIView):
	permission_classes = [IsAuthenticated]
	serializer_class = MatchSerializer

	def get_queryset(self):
		user = self.request.user
		return Match.objects.filter(Q(player1=user.id) | Q(player2=user.id)).order_by('-id')
	
class MatchStartView(APIView):
	def get(self, request, pk):
		try:
			match = get_object_or_404(Match, pk=pk)
			match_serializer = MatchStartSerializer(match)
			return Response(match_serializer.data)
		except Http404:
			return Response({'detail' : 'Match not found'}, status=status.HTTP_404_NOT_FOUND)
	
class ActiveFriendshipsListView(ListAPIView):
	serializer_class = FriendshipListSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		return Friendship.objects.filter(Q(sender=user.id) | Q(receiver=user.id), Q(status=Friendship.StatusOptions.ACCEPTED)).order_by('-id')

class FriendshipRequestSentListView(ListAPIView):
	serializer_class = FriendshipListSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		return Friendship.objects.filter(Q(sender=user.id), Q(status=Friendship.StatusOptions.PENDING)).order_by('-id')
	
class FriendshipRequestReceivedListView(ListAPIView):
	serializer_class = FriendshipListSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		return Friendship.objects.filter(Q(receiver=user.id), Q(status=Friendship.StatusOptions.PENDING)).order_by('-id')

class FriendshipRequestView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, username):
		target_player_name = username
		if not target_player_name:
			return Response({'detail' : 'Receiver\'s username not specified'}, status=status.HTTP_400_BAD_REQUEST)
		elif target_player_name == request.user.username:
			return Response({'detail' : 'You cannot befriend yourself'}, status=status.HTTP_400_BAD_REQUEST)
		try:
			target_player = CustomUser.objects.get(username=target_player_name)
		except CustomUser.DoesNotExist:
			return Response({'detail' : 'User not found'}, status=status.HTTP_404_NOT_FOUND)
		sender_current = request.user
		receiver_current = target_player
		print("Sender: ", sender_current.id, " Receiver: ", receiver_current.id)
		db_check = Friendship.objects.filter(Q(receiver=sender_current) | Q(sender=sender_current), Q(receiver=receiver_current) | Q(sender=receiver_current))
		if db_check:
			return Response({'detail': 'Friendship (request) already exists.'}, status=status.HTTP_400_BAD_REQUEST)
		# the friendship gets created here and so the database needs data in this format
		friendship_data = {
			'sender': sender_current.id,
			'receiver': receiver_current.id
		}
		friendship_serializer = FriendshipSerializer(data=friendship_data)
		if friendship_serializer.is_valid():
			friendship_serializer.save()
			return Response({'detail': 'Friendship request sent successfully.', 'friendship_id': friendship_serializer.data['id']}, status=status.HTTP_201_CREATED)
		else:
			return Response(friendship_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# https://stackoverflow.com/questions/30449960/django-save-vs-update-to-update-the-database
# https://stackoverflow.com/questions/17159471/how-to-use-select-for-update-to-get-an-object-in-django
class FriendshipRequestAcceptView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, pk):
		try:
			friendship =  get_object_or_404(Friendship, pk=pk)
			if (friendship.receiver != request.user) or (friendship.status != Friendship.StatusOptions.PENDING):
				raise Http404
			friendship.status = Friendship.StatusOptions.ACCEPTED
			friendship.save()
			return Response({'detail': 'Friendship request accepted successfully.'}, status=status.HTTP_200_OK)
		except Http404:
			return Response({'detail': 'Friendship request not found.'}, status=status.HTTP_404_NOT_FOUND)
	
class FriendshipRequestRefuseView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, pk):
		try:
			friendship =  get_object_or_404(Friendship, pk=pk)
			if (friendship.receiver != request.user) or (friendship.status != Friendship.StatusOptions.PENDING):
				raise Http404
			friendship.delete()
			return Response({'detail': 'Friendship request deleted successfully.'}, status=status.HTTP_200_OK)
		except Http404:
			return Response({'detail': 'Friendship request not found.'}, status=status.HTTP_404_NOT_FOUND)

class FriendshipRequestDeleteView(APIView):
	permission_classes = [IsAuthenticated]

	def delete(self, request, pk):
		try:
			friendship = get_object_or_404(Friendship, pk=pk)
			if (friendship.sender != request.user and friendship.receiver != request.user)\
				or (friendship.status != Friendship.StatusOptions.ACCEPTED and friendship.sender != request.user):
				raise Http404
			friendship.delete()
			return Response({'detail': 'Friendship (request) deleted successfully.'}, status=status.HTTP_200_OK)
		except Http404:
			return Response({'detail': 'Friendship not found.'}, status=status.HTTP_404_NOT_FOUND)

