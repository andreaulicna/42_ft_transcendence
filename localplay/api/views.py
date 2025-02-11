from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from localplay.settings import GAME_CONSTANTS
from .serializers import LocalMatchSerializer
from .models import CustomUser, LocalMatch
from django.utils.translation import gettext as _

def csrf_failure(request, reason=""):
	return Response({'detail' : _('CSRF token missing')}, status=status.HTTP_403_FORBIDDEN)

class HealthCheckView(APIView):
	def get(self, request):
		return Response({'detail' : 'Healthy'})

def set_match_data(creator_id, player1_username, player2_username):
	data = {
				'creator' : creator_id,
				'default_ball_size' : GAME_CONSTANTS['BALL_SIZE'],
				'default_paddle_height' : GAME_CONSTANTS['PADDLE_HEIGHT'],
				'default_paddle_width' : GAME_CONSTANTS['PADDLE_WIDTH'],
				'default_paddle_speed' : GAME_CONSTANTS['PADDLE_SPEED'],
				'player1_tmp_username' : player1_username,
				'player2_tmp_username' : player2_username,
			}
	return (data)

def get_prev_match(prev_match_id):
	try:
		prev_match = LocalMatch.objects.get(id=prev_match_id)
		return prev_match
	except LocalMatch.DoesNotExist:
		return None

def get_player_state(player_id):
	try:
		user = CustomUser.objects.get(id=player_id)
		return user.state
	except CustomUser.DoesNotExist:
		return None

class CreateMatchView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		creator = request.user
		if get_player_state(creator.id) == CustomUser.StateOptions.INGAME:
			return Response({'detail' : _('Player already has a match in progress.')}, status=status.HTTP_403_FORBIDDEN)
		player1_username = request.data.get('player1_tmp_username', 'player1')
		player2_username = request.data.get('player2_tmp_username', 'player2')
		if player1_username == player2_username:
			return Response({'detail' : _('Usernames cannot be identical')}, status=status.HTTP_400_BAD_REQUEST)
		data = set_match_data(creator.id, player1_username, player2_username)
		match_serializer = LocalMatchSerializer(data=data)
		if match_serializer.is_valid():
			match_serializer.save()
			return Response({'detail': _('Local match created and ready to play.'), 'match_id': match_serializer.data['id']}, status=status.HTTP_201_CREATED)
		else:
			return Response(match_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateRematchView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, prev_match_id, sides_mode):
		prev_match = get_prev_match(prev_match_id)
		if (prev_match is None):
			return Response({'detail' : _('Previous match to base this rematch on does not exist.')}, status=status.HTTP_404_NOT_FOUND)
		creator = request.user
		if (sides_mode == "keep"):
			data = set_match_data(creator.id, prev_match.player1_tmp_username, prev_match.player2_tmp_username)
		elif (sides_mode == "switch"):
			data = set_match_data(creator.id, prev_match.player2_tmp_username, prev_match.player1_tmp_username)
		match_serializer = LocalMatchSerializer(data=data)
		if match_serializer.is_valid():
			match_serializer.save()
			return Response({'detail': _('Rematch for a local match created and ready to play.'), 'match_id': match_serializer.data['id']}, status=status.HTTP_201_CREATED)
		else:
			return Response(match_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

