from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ai_play.settings import GAME_CONSTANTS
from .serializers import AIMatchSerializer
from .models import CustomUser
from django.utils.translation import gettext as _

class HealthCheckView(APIView):
	def get(self, request):
		return Response({'detail' : 'Healthy'})

def get_player_state(player_id):
	try:
		user = CustomUser.objects.get(id=player_id)
		return user.state
	except CustomUser.DoesNotExist:
		return None
	
class CreateAIMatchView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		creator = request.user
		if get_player_state(creator.id) == CustomUser.StateOptions.INGAME:
			return Response({'detail' : 'Player already has a match in progress.'}, status=status.HTTP_403_FORBIDDEN)
		data = {
				'creator' : creator.id,
				'default_ball_size' : GAME_CONSTANTS['BALL_SIZE'],
				'default_paddle_height' : GAME_CONSTANTS['PADDLE_HEIGHT'],
				'default_paddle_width' : GAME_CONSTANTS['PADDLE_WIDTH'],
				'default_paddle_speed' : GAME_CONSTANTS['PADDLE_SPEED'],
			}
		match_serializer = AIMatchSerializer(data=data)
		if match_serializer.is_valid():
			match_serializer.save()
			return Response({'detail': _('AI match created and ready to play.'), 'match_id': match_serializer.data['id']}, status=status.HTTP_201_CREATED)
		else:
			return Response(match_serializer.errors, status=status.HTTP_400_BAD_REQUEST)