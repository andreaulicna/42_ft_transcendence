from .models import Tournament, PlayerTournament, CustomUser, Match, LocalTournament
from .serializers import TournamentSerializer, PlayerTournamentSerializer, WaitingTournamentSerializer, LocalTournamentSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListAPIView
from pathlib import Path
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework.generics import RetrieveAPIView
from django.utils.translation import gettext as _

def csrf_failure(request, reason=""):
	return Response({'detail' : _('CSRF token missing')}, status=status.HTTP_403_FORBIDDEN)

class HealthCheckView(APIView):
	def get(self, request):
		return Response({'detail' : 'Healthy'})

def player_already_in_waiting_tournament(tournaments, player_id):
	for tournament_iterator in tournaments:
		players_in_tournament = PlayerTournament.objects.filter(tournament=tournament_iterator.id)
		for player in players_in_tournament:
			if player.player_id == player_id:
				return True
	return False

def player_already_in_inprogress_tournament(tournaments, player_id):
	for tournament_iterator in tournaments:
		players_in_tournament = PlayerTournament.objects.filter(tournament=tournament_iterator.id)
		for player in players_in_tournament:
			all_tournament_matches = Match.objects.filter(tournament=tournament_iterator.id)
			if len(all_tournament_matches) == tournament_iterator.capacity - 1:
				return True
			for match in all_tournament_matches:
				if (player.id in [match.player1_id, match.player2_id]) and (match.status != Match.StatusOptions.FINISHED):
					return True
	return False

def get_player_state(player_id):
	try:
		user = CustomUser.objects.get(id=player_id)
		return user.state
	except CustomUser.DoesNotExist:
		return None

class CreateTournamentView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, *args, **kwargs):
		# Check max. capacity
		capacity = self.kwargs.get('capacity')
		print(f"Capacity in create view: {capacity}")

		# User INGAME in other game mode
		creator = request.user
		if get_player_state(creator.id) == CustomUser.StateOptions.INGAME:
			return Response({'detail' : _('Player already has a match in progress.')}, status=status.HTTP_403_FORBIDDEN)
		# Get all waiting tournaments
		waiting_tournaments = Tournament.objects.filter(status=Tournament.StatusOptions.WAITING)
		# Allow only one waiting tournament
		if player_already_in_waiting_tournament(waiting_tournaments, request.user.id):
			return Response({"details" : _("You are already in a waiting tournament, you cannot create another one!")}, status=status.HTTP_403_FORBIDDEN)
		# Get all inprogress tournaments
		inprogress_tournaments = Tournament.objects.filter(status=Tournament.StatusOptions.INPROGRESS)
		# Allow only one in-progress tournament
		if player_already_in_inprogress_tournament(inprogress_tournaments, request.user.id):
			return Response({"details" : _("You are already in a tournament and have matches to play, you cannot create another one!")}, status=status.HTTP_403_FORBIDDEN)

		try:
			creator = CustomUser.objects.get(username=request.user)
		except CustomUser.DoesNotExist:
			return Response({'detail': _('Player does not exist')}, status=status.HTTP_404_NOT_FOUND)
		
		tournament_data = {
			'creator' : creator.id,
			'capacity' : capacity
		}
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
			return Response({'detail': _('Tournament created.'), 
					   		'tournament': tournament_serializer.data},
							status=status.HTTP_201_CREATED)
		else:
			return Response(player_tournament_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JoinTournamentView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, *args, **kwargs):
		# Get data from the request and URL parameters
		player_tmp_username = request.data.get('player_tmp_username')
		tournament_id = self.kwargs.get('tournament_id')

		# Get all waiting tournaments
		waiting_tournaments = Tournament.objects.filter(status=Tournament.StatusOptions.WAITING)
		# Allow only one waiting tournament
		if player_already_in_waiting_tournament(waiting_tournaments, request.user.id):
			return Response({"details" : _("You are alredy in a waiting tournament, you cannot join another one!")}, status=status.HTTP_403_FORBIDDEN)
		# Get all inprogress tournaments
		inprogress_tournaments = Tournament.objects.filter(status=Tournament.StatusOptions.INPROGRESS)
		# Allow only one in-progress tournament
		if player_already_in_inprogress_tournament(inprogress_tournaments, request.user.id):
			return Response({"details" : _("You are already in a tournament and have matches to play!")}, status=status.HTTP_403_FORBIDDEN)
		# Add to tournament based on id
		try:
			tournament_to_join = Tournament.objects.get(id=tournament_id)
		except Tournament.DoesNotExist:
			return Response({"details" : _("No such tournament exists!")}, status=status.HTTP_404_NOT_FOUND)
		
		players_in_tournament_to_join = PlayerTournament.objects.filter(tournament=tournament_to_join.id)
		if (len(players_in_tournament_to_join) >= tournament_to_join.capacity):
			return Response({"details" : _("This tournament is already full!")}, status=status.HTTP_403_FORBIDDEN)
		player_tournament_data = {
			'player' : request.user.id,
			'tournament' : tournament_to_join.id
		}
		if player_tmp_username:
			player_tournament_data['player_tmp_username'] = player_tmp_username
		player_tournament_serializer = PlayerTournamentSerializer(data=player_tournament_data)
		if player_tournament_serializer.is_valid():
			player_tournament_serializer.save()
			return Response({'detail': _('Added you to the tournament!.'), 
					   		'tournament': TournamentSerializer(tournament_to_join).data,},
							status=status.HTTP_201_CREATED)
		else:
			return Response(player_tournament_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CancelJoinTournamentView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, *args, **kwargs):
		tournament_id = self.kwargs.get('tournament_id')
		user_id = request.user.id

		try:
			tournament_to_cancel_join = Tournament.objects.get(id=tournament_id)
		except Tournament.DoesNotExist:
			return Response({"details": _("No such tournament exists!")}, status=status.HTTP_404_NOT_FOUND)

		if tournament_to_cancel_join.status == Tournament.StatusOptions.INPROGRESS:
			return Response({"details": _("This tournament is already in progress, you cannot cancel joining!")}, status=status.HTTP_403_FORBIDDEN)
		if tournament_to_cancel_join.status == Tournament.StatusOptions.FINISHED:
			return Response({"details": _("This tournament has already finished, you cannot cancel joining!")}, status=status.HTTP_403_FORBIDDEN)

		try:
			tournament_in_return = TournamentSerializer(tournament_to_cancel_join).data
			if (user_id == tournament_to_cancel_join.creator.id):
				player_delete = PlayerTournament.objects.filter(tournament=tournament_id)
				for player in player_delete:
					player.delete()
				tournament_to_cancel_join.delete()
			else:
				player_tournament = PlayerTournament.objects.get(player=user_id, tournament=tournament_id)
				player_tournament.delete()
			return Response({"details": _("You have successfully canceled joining the tournament."),
					   		'tournament': tournament_in_return,},
							status=status.HTTP_200_OK)
		except PlayerTournament.DoesNotExist:
			return Response({"details": _("You are not part of this tournament.")}, status=status.HTTP_404_NOT_FOUND)
		
class WaitingTournamentsListView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		waiting_tournaments = Tournament.objects.filter(status=Tournament.StatusOptions.WAITING)
		serializer = WaitingTournamentSerializer(waiting_tournaments, many=True)
		return Response(serializer.data)
class TournamentListOfPlayerView(ListAPIView):
	serializer_class = TournamentSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		return Tournament.objects.filter(playertournament__player=user).distinct()

class TournamentInfoView(RetrieveAPIView):
	serializer_class = TournamentSerializer
	permission_classes = [IsAuthenticated]

	def get_object(self):
		tournament_id = self.kwargs.get('tournament_id')
		try:
			return Tournament.objects.get(id=tournament_id)
		except Tournament.DoesNotExist:
			raise Http404(_("No such tournament exists!"))

def get_players_based_on_capacity(request, capacity):
	if 'players' not in request.data:
		return Response({'detail': 'Missing players key in the request data.'}, status=status.HTTP_400_BAD_REQUEST)
	players = request.data.get('players', [])
	if len(players) != capacity:
		raise ValueError(_("Wrong number of players for the tournament capacity"))
	return players[:capacity]
	
class CreateLocalTournamentView(APIView):

	permission_classes = [IsAuthenticated]

	def post(self, request, *args, **kwargs):
		# Check max. capacity
		capacity = self.kwargs.get('capacity')
		print(f"Capacity in create view for local tournament: {capacity}")

		# User INGAME in other game mode
		creator_player = request.user
		if get_player_state(creator_player.id) == CustomUser.StateOptions.INGAME:
			return Response({'detail' : _('Player already has a match in progress.')}, status=status.HTTP_403_FORBIDDEN)

		# Get all waiting and in_progress tournaments
		tournament_to_check = LocalTournament.objects.filter(Q(status=LocalTournament.StatusOptions.WAITING) | Q(status=LocalTournament.StatusOptions.INPROGRESS), Q(creator=creator_player.id)).exists()
		if tournament_to_check:
			return Response({"details" : _("You are already playing a local tournament, you cannot create another one!")}, status=status.HTTP_403_FORBIDDEN)

		try:
			players = get_players_based_on_capacity(request, capacity)
		except ValueError as e:
			return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
		local_tournament_data = {
			'creator': creator_player.id,
			'capacity': capacity,
			'players': players
		}
		local_tournament_name = request.data.get('tournament_name')
		if local_tournament_name:
			local_tournament_data['name'] = local_tournament_name
		local_tournament_serializer = LocalTournamentSerializer(data=local_tournament_data)
		if local_tournament_serializer.is_valid():
			local_tournament_serializer.save()
			return Response({'detail': _('Local tournament created.'),
							'local_tournament': local_tournament_serializer.data},
							status=status.HTTP_201_CREATED)
		else:
			return Response(local_tournament_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

