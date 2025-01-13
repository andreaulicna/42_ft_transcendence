from .models import CustomUser, Match, LocalMatch, AIMatch, Friendship
from .serializers import (
	UserSerializer, OtherUserSerializer,
	MatchSerializer, 
	FriendshipSerializer, FriendshipListSerializer, UsersStatusListSerializer,
	MatchStartSerializer, LocalMatchStartSerializer, AIMatchStartSerializer, 
	HistoryAIMatchSerializer, HistoryLocalMatchSerializer, HistoryMatchSerializer,
	WinLossSerializer
)
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
import pyotp, qrcode, logging, io
from django.db import models, IntegrityError
from django.core.exceptions import ValidationError


class HealthCheckView(APIView):
	def get(self, request):
		return Response({'detail' : 'Healthy'})

class UserRegistrationView(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		serializer = UserSerializer(data=request.data)
		# request.data['two_factor_secret'] = pyotp.random_base32() #might be moved somewhere else
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class QRCodeView(APIView):
# 	permission_classes = [IsAuthenticated]
	
# 	def get(self, request):
# 		user = request.user
# 		otp_uri = pyotp.totp.TOTP(user.two_factor_secret).provisioning_uri(name=user.username, issuer_name='42praguescendence')
# 		qr = qrcode.make(otp_uri)
# 		buffer = io.BytesIO()
# 		qr.save(buffer, format="png")
# 		buffer.seek(0)
# 		qr_code = base64.b64encode(buffer.getvalue()).decode("utf-8")
# 		qr_code_data_uri = f"data:image/png;base64,{qr_code}"
# 		return Response({"qr_code" : qr_code_data_uri})

class Enable2FA(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		user = request.user
		if user.two_factor_secret is None:
			user.two_factor_secret = pyotp.random_base32()
			user.save()
		otp_uri = pyotp.totp.TOTP(user.two_factor_secret).provisioning_uri(name=user.username, issuer_name='42praguescendence')
		qr = qrcode.make(otp_uri)
		buffer = io.BytesIO()
		qr.save(buffer, format="png")
		buffer.seek(0)
		qr_code = base64.b64encode(buffer.getvalue()).decode("utf-8")
		qr_code_data_uri = f"data:image/png;base64,{qr_code}"
		return Response({"qr_code" : qr_code_data_uri})

	def post(self, request):
		user = request.user
		otp_code = request.data.get('otp_code', None)

		if not otp_code:
			return Response({'detail' : 'OTP not provided'}, status=status.HTTP_400_BAD_REQUEST)
		
		if not user.two_factor_secret:
			return Response({'detail' : 'Secret has not been generated yet'}, status=status.HTTP_400_BAD_REQUEST)
		
		totp = pyotp.TOTP(user.two_factor_secret)
		if totp.verify(otp_code):
			user.two_factor = True
			user.save()
			return Response({'detail' : '2FA enabled'})
		
		return Response({'detail' : 'Invalid OTP'}, status=status.HTTP_403_FORBIDDEN)
	
class Disable2FA(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		user = request.user
		if user.two_factor:
			otp_code = request.data.get('otp_code', None)

			if not otp_code:
				return Response({'detail' : 'OTP not provided'}, status=status.HTTP_400_BAD_REQUEST)
			
			totp = pyotp.TOTP(user.two_factor_secret)
			if totp.verify(otp_code):
				user.two_factor = False
				user.two_factor_secret = None
				user.save()
				return Response({'detail' : '2FA disabled'})
			
			return Response({'detail' : 'Invalid OTP'}, status=status.HTTP_403_FORBIDDEN)
		
		return Response({'detail' : '2FA has not been enabled'}, status=status.HTTP_400_BAD_REQUEST)

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
			username = request.data.get('username')
			try:
				if first_name:
					new_first_name = ' '.join(first_name.split())
					player.first_name = new_first_name
				if last_name:
					new_last_name = ' '.join(last_name.split())
					player.last_name = new_last_name
				if username:
					new_username = ' '.join(username.split())
					player.username = new_username
				player.full_clean()
				player.save()
			except IntegrityError as e:
				return Response({'detail': 'Username already exists, choose a different one'}, status=status.HTTP_400_BAD_REQUEST)
			except ValidationError as e:
				return Response({"details" : str(e)},status=status.HTTP_400_BAD_REQUEST)
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
		data = request.data.get('profilePic')
		if not data:
			return Response({'detail': 'No avatar data provided'}, status=status.HTTP_400_BAD_REQUEST)
		try:
			format, imgstr = data.split(';base64,')
			ext = format.split('/')[-1] 
			avatar_data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
			# Define the folder where the avatar is stored
			if player.avatar:
				# Delete existing files in the folder
				avatar_folder = os.path.dirname(player.avatar.path)
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

class LocalMatchStartView(APIView):
	def get(self, request, pk):
		try:
			match = get_object_or_404(LocalMatch, pk=pk)
			match_serializer = LocalMatchStartSerializer(match)
			return Response(match_serializer.data)
		except Http404:
			return Response({'detail' : 'Match not found'}, status=status.HTTP_404_NOT_FOUND)

class AIMatchStartView(APIView):
	def get(self, request, pk):
		try:
			match = get_object_or_404(AIMatch, pk=pk)
			match_serializer = AIMatchStartSerializer(match)
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

class MatchHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        # Get all matches that are FINISHED per type
        matches = Match.objects.filter(
            (models.Q(player1=user) | models.Q(player2=user)) & models.Q(status=Match.StatusOptions.FINISHED)
        )
        local_matches = LocalMatch.objects.filter(
            models.Q(creator=user) & models.Q(status=Match.StatusOptions.FINISHED)
        )
        ai_matches = AIMatch.objects.filter(
            models.Q(creator=user) & models.Q(status=Match.StatusOptions.FINISHED)
        )

        # Serialize each category of matches
        match_serializer = HistoryMatchSerializer(matches, many=True)
        local_match_serializer = HistoryLocalMatchSerializer(local_matches, many=True)
        ai_match_serializer = HistoryAIMatchSerializer(ai_matches, many=True)

        # Combine the serialized data into the desired structure
        response_data = {
            'remote_matches': match_serializer.data,
            'local_matches': local_match_serializer.data,
            'ai_matches': ai_match_serializer.data,
        }

        return Response(response_data)

class WinLossView(APIView):
    # Remote + AI matches only as for Local we cannot really distinguish which player is the user
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        data = WinLossSerializer.count_win_loss(user)
        serializer = WinLossSerializer(data)
        return Response(serializer.data)

class UsersStatusListView(ListAPIView):
	serializer_class = UsersStatusListSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		return CustomUser.objects.exclude(id=user.id).order_by('-id')
