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

def player_already_in_a_tournament(tournaments, player_id):
    for tournament_iterator in tournaments:
        players_in_tournament = PlayerTournament.objects.filter(tournament=tournament_iterator.id)
        for player in players_in_tournament:
            if player.player_id == player_id:
                return True
    return False
class JoinTournamentView(APIView):
	permission_classes = [IsAuthenticated]
	def post(self, request):
		# Get data from the request
		player_tmp_username = request.data.get('player_tmp_username')
		tournament_name = request.data.get('tournament_name')

		# Allow only one waiting or in-progress tournament
		waiting_and_inprogress_tournament = Tournament.objects.filter(
			Q(status=Tournament.StatusOptions.WAITING) | Q(status=Tournament.StatusOptions.INPROGRESS)
		)
		if player_already_in_a_tournament(waiting_and_inprogress_tournament, request.user.id) == True:
			return Response({"details" : "You are alredy in a (waiting or in progress) tournament!"}, status=status.HTTP_403_FORBIDDEN)

		# Get all waiting tournaments
		waiting_tournaments = Tournament.objects.filter(status=Tournament.StatusOptions.WAITING)
		# Try to find a tournament to join 
		for waiting_tournament in waiting_tournaments: 
			players_in_tournament = PlayerTournament.objects.filter(tournament=waiting_tournament.id)
			# If there was a tournament_name supplied, assume tournament between friends
			if (tournament_name is not None):
				if (waiting_tournament.name != tournament_name):
					continue
				if (len(players_in_tournament) == 4): # CHANGE to tournament capacity
					return Response({'detail': 'The requested tournament is already full!'}, status=status.HTTP_200_OK)
				player_tournament_data = {'player' : request.user.id,
										'tournament' : waiting_tournament.id}
				if player_tmp_username:
					player_tournament_data['player_tmp_username'] = player_tmp_username
				player_tournament_serializer = PlayerTournamentSerializer(data=player_tournament_data)
				if player_tournament_serializer.is_valid():
					player_tournament_serializer.save()
				else:
					return Response(player_tournament_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
				return Response({'detail': 'You can join your friends at this tournament!.', 
						   		'tournament': TournamentSerializer(waiting_tournament).data,
								'player_tournament' : player_tournament_serializer.data},
								status=status.HTTP_200_OK)
			# If there wasn't a tournament_name supplied, asuume random tournament
			elif (len(players_in_tournament) < 4): # CHANGE to tournament capacity
				player_tournament_data = {'player' : request.user.id,
										'tournament' : waiting_tournament.id}
				if player_tmp_username:
					player_tournament_data['player_tmp_username'] = player_tmp_username
				player_tournament_serializer = PlayerTournamentSerializer(data=player_tournament_data)
				if player_tournament_serializer.is_valid():
					player_tournament_serializer.save()
				else:
					return Response(player_tournament_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
				return Response({'detail': 'Found a tournamet to join for you!.', 
						   		'tournament': TournamentSerializer(waiting_tournament).data,
								'player_tournament' : player_tournament_serializer.data},
								status=status.HTTP_200_OK)
		if tournament_name:
			return Response({'detail': 'There is no tournament with such a name. You need to create it to play with your friends!'}, status=status.HTTP_200_OK)
		return Response({'detail': 'You need to create a tournament to join!'}, status=status.HTTP_200_OK)
		
class TournamentListView(ListAPIView):
	serializer_class = TournamentSerializer
	permission_classes = [IsAuthenticated]
	queryset = Tournament.objects.all()

class PlayerTournamentListView(ListAPIView):
	serializer_class = PlayerTournamentSerializer
	permission_classes = [IsAuthenticated]
	queryset = PlayerTournament.objects.all()
