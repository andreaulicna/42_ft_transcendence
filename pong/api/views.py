from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timezone import now
from rest_framework.permissions import AllowAny
from django.utils.translation import gettext as _
from rest_framework import status
from .models import Match, CustomUser
from django.db.models import Q
from rest_framework import status


def csrf_failure(request, reason=""):
	return Response({'detail' : _('CSRF token missing')}, status=status.HTTP_403_FORBIDDEN)

class HealthCheckView(APIView):
	def get(self, request):
		return Response({'detail' : 'Healthy'})
	
class CurrentServerTimeView(APIView):
	permission_classes = [AllowAny]
	def get(self, request):
		return Response({'server_time' : now().isoformat()})

class MatchesInProgressView(APIView):
	def get(self, request):
		player = request.user
		player_id = request.user.id
		try:
			if player.state == CustomUser.StateOptions.INGAME:
				return Response({'match_id' : 'User is already playing something else'}, status=status.HTTP_403_FORBIDDEN)
			match_database = Match.objects.get(
				(Q(player1=player_id) | Q(player2=player_id)) & Q(status=Match.StatusOptions.INPROGRESS))
			return Response({'match_id' : match_database.id})
		except Match.DoesNotExist:
				return Response({'match_id' : 0})
		except Match.MultipleObjectsReturned:
			match_database = Match.objects.filter(
				(Q(player1=player_id) | Q(player2=player_id)) & Q(status=Match.StatusOptions.INPROGRESS)).latest()
			return Response({'match_id' : match_database.id})
