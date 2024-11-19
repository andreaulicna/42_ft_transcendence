from .models import Tournament, PlayerTournament, CustomUser
from .serializers import TournamentSerializer, PlayerTournamentSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListAPIView
from pathlib import Path
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import Http404

class CreateTournamentView(APIView):
	permission_classes = [IsAuthenticated]
	def post(self, request):
		try:
			creator = CustomUser.objects.get(username=request.user)
		except CustomUser.DoesNotExist:
			return Response({'detail': 'Player does not exist'}, status=status.HTTP_404_NOT_FOUND)
		
		tournament_data = {'creator' : creator.id}
		tournament_name = request.data.get('tournament_name')
		if tournament_name:
			tournament_data['name'] = tournament_name
		tournament_serializer = TournamentSerializer(data=tournament_data)
		if tournament_serializer.is_valid():
			tournament = tournament_serializer.save()
		else:
			return Response(tournament_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		
		### The following logic immediately creates a user-specific table for the creator,
		### which means they automatically join the tournament as player1
		player_tournament_data = {'player' : tournament.creator.id,
								'tournament' : tournament.id}
		player_tmp_username = request.data.get('player_tmp_username')
		if player_tmp_username:
			player_tournament_data['player_tmp_username'] = player_tmp_username
		player_tournament_serializer = PlayerTournamentSerializer(data=player_tournament_data)
		if player_tournament_serializer.is_valid():
			player_tournament_serializer.save()
		else:
			return Response(player_tournament_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		return Response({'detail': 'Tournament created.', 
				   		'tournament': tournament_serializer.data,
						'player_tournament' : player_tournament_serializer.data},
						status=status.HTTP_201_CREATED)

		
class TournamentListView(ListAPIView):
	serializer_class = TournamentSerializer
	permission_classes = [IsAuthenticated]
	queryset = Tournament.objects.all()
