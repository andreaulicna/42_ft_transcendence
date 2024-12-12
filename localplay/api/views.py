from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from localplay.settings import GAME_CONSTANTS
from .serializers import LocalMatchSerializer
from .models import Match

class HealthCheckView(APIView):
	def get(self, request):
		return Response({'detail' : 'Healthy'})

class CreateMatchView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		creator = request.user
		player1_username = request.data.get('player1_tmp_username', 'player1')
		player2_username = request.data.get('player2_tmp_username', 'player2')
		if player1_username == player2_username:
			return Response({'detail' : 'Usernames cannot be identical'}, status=status.HTTP_400_BAD_REQUEST)
		data = {
				'creator' : creator.id,
				'default_ball_size' : GAME_CONSTANTS['BALL_SIZE'],
				'default_paddle_height' : GAME_CONSTANTS['PADDLE_HEIGHT'],
				'default_paddle_width' : GAME_CONSTANTS['PADDLE_WIDTH'],
				'default_paddle_speed' : GAME_CONSTANTS['PADDLE_SPEED'],
				'player1_tmp_username' : request.data.get('player1_tmp_username', 'player1'),
				'player2_tmp_username' : request.data.get('player2_tmp_username', 'player2'),
			}
		match_serializer = LocalMatchSerializer(data=data)
		if match_serializer.is_valid():
			match_serializer.save()
			return Response({'detail': 'Local match created and ready to play.', 'match_id': match_serializer.data['id']}, status=status.HTTP_201_CREATED)
		else:
			return Response(match_serializer.errors, status=status.HTTP_400_BAD_REQUEST)