from rest_framework import serializers
from .models import CustomUser, Match, LocalMatch, AIMatch, Friendship
from django.db.models import Q
from django.db import models
from django.utils.translation import gettext_lazy as _



class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = '__all__' # returns all parameters
		extra_kwargs = {'password' : {'write_only': True}, 
						'two_factor_secret' : {'write_only' : True}} # protects GET user/info/ from exposing the hash of the password in the response

	def create(self, validated_data):
		user = CustomUser.objects.create_user(**validated_data)
		return user

	def validate_username(self, value):
		if len(value) < 3:
			raise serializers.ValidationError(_("Username is too short"))
		elif len(value) > 20:
			raise serializers.ValidationError(_("Username is too long"))
		return value

class OtherUserSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ['id', 'username', 'win_count', 'loss_count', 'avatar']
	
class MatchSerializer(serializers.ModelSerializer):
	#match = serializers.SerializerMethodField()
	class Meta:
		model = Match
		fields = '__all__' # returns all parameters

	def create(self, validated_data):
		match = Match.objects.create(**validated_data)
		return match

class MatchStartSerializer(serializers.ModelSerializer):
	class Meta:
		model = Match
		fields = ['id', 
				'player1', 
				'player2', 
				'default_ball_size', 
				'default_paddle_height', 
				'default_paddle_width', 
				'default_paddle_speed']

	def create(self, validated_data):
		match = Match.objects.create(**validated_data)
		return match

class LocalMatchStartSerializer(serializers.ModelSerializer):
	class Meta:
		model = LocalMatch
		fields = ['id', 
				'player1_tmp_username', 
				'player2_tmp_username', 
				'default_ball_size', 
				'default_paddle_height', 
				'default_paddle_width', 
				'default_paddle_speed']

	def create(self, validated_data):
		match = LocalMatch.objects.create(**validated_data)
		return match

class AIMatchStartSerializer(serializers.ModelSerializer):
	class Meta:
		model = AIMatch
		fields = ['id', 
				'creator', 
				'default_ball_size', 
				'default_paddle_height', 
				'default_paddle_width', 
				'default_paddle_speed']

	def create(self, validated_data):
		match = AIMatch.objects.create(**validated_data)
		return match

class FriendshipSerializer(serializers.ModelSerializer):
	class Meta:
		model = Friendship
		fields = '__all__' # returns all parameters

	def create(self, validated_data):
		friendship = Friendship.objects.create(**validated_data)
		return friendship

class FriendshipListSerializer(serializers.ModelSerializer):
	friend_id = serializers.SerializerMethodField()
	friend_status = serializers.SerializerMethodField()
	friend_username = serializers.SerializerMethodField()

	class Meta:
		model = Friendship
		fields = ['id', 'friend_id', 'friend_username', 'friend_status']

	def get_friend(self, obj):
		user = self.context['request'].user
		if (user.id != obj.sender.id):
			return CustomUser.objects.get(id=obj.sender.id)
		return CustomUser.objects.get(id=obj.receiver.id)

	def get_friend_id(self, obj):
		friend = self.get_friend(obj)
		return friend.id

	def get_friend_username(self, obj):
		friend = self.get_friend(obj)
		return friend.username

	def get_friend_status(self, obj):
		friend = self.get_friend(obj)
		if friend.status_counter > 0:
			return "ON"
		return "OFF"

class HistoryMatchSerializer(serializers.ModelSerializer):
	player1_username = serializers.CharField(source='player1.username', read_only=True)
	player2_username = serializers.CharField(source='player2.username', read_only=True)
	player1_id = serializers.IntegerField(source='player1.id', read_only=True)
	player2_id = serializers.IntegerField(source='player2.id', read_only=True)
	date = serializers.DateTimeField(source='time_created')
	type = serializers.SerializerMethodField()

	class Meta:
		model = Match
		fields = ['id', 'player1_username', 'player2_username', 'player1_id', 'player2_id', 'player1_score', 'player2_score', 'date', 'type']

	def get_type(self, obj):
		return 'RemoteMatch'


class HistoryLocalMatchSerializer(serializers.ModelSerializer):
	player1_username = serializers.CharField(source='player1_tmp_username', read_only=True)
	player2_username = serializers.CharField(source='player2_tmp_username', read_only=True)
	creator_id = serializers.CharField(source='creator.id', read_only=True)
	date = serializers.DateTimeField(source='time_created')
	type = serializers.SerializerMethodField()

	class Meta:
		model = LocalMatch
		fields = ['id', 'player1_username', 'player2_username', 'player1_score', 'player2_score', 'date', 'type', 'creator_id']

	def get_type(self, obj):
		return 'LocalMatch'

class HistoryAIMatchSerializer(serializers.ModelSerializer):
	player1_username = serializers.CharField(source='creator.username', read_only=True)
	player2_username = serializers.SerializerMethodField()
	creator_id = serializers.CharField(source='creator.id', read_only=True)
	date = serializers.DateTimeField(source='time_created')
	type = serializers.SerializerMethodField()

	class Meta:
		model = AIMatch
		fields = ['id', 'player1_username', 'player2_username', 'player1_score', 'player2_score', 'date', 'type', 'creator_id']

	def get_player2_username(self, obj):
		return 'AI'
	
	def get_type(self, obj):
		return 'AIMatch'

class WinLossSerializer(serializers.Serializer):
	overall_win = serializers.IntegerField()
	overall_loss = serializers.IntegerField()
	remote_match_win = serializers.IntegerField()
	remote_match_loss = serializers.IntegerField()
	ai_match_win = serializers.IntegerField()
	ai_match_loss = serializers.IntegerField()

	class Meta:
		fields = ['overall_win', 'overall_loss', 'remote_match_win', 'remote_match_loss', 'ai_match_win', 'ai_match_loss']

	@staticmethod
	def count_win_loss(user):
		overall_win = 0
		overall_loss = 0
		remote_match_win = 0
		remote_match_loss = 0
		ai_match_win = 0
		ai_match_loss = 0

		# Count wins and losses for Match
		matches = Match.objects.filter(
			(Q(player1=user) | Q(player2=user)) & Q(status=Match.StatusOptions.FINISHED)
		)
		for match in matches:
			if match.winner == user:
				remote_match_win += 1
				overall_win += 1
			else:
				remote_match_loss += 1
				overall_loss += 1

		# Count wins and losses for AIMatch
		ai_matches = AIMatch.objects.filter(
			Q(creator=user) & Q(status=Match.StatusOptions.FINISHED)
		)
		for match in ai_matches:
			if match.winner == user.username:
				ai_match_win += 1
				overall_win += 1
			else:
				ai_match_loss += 1
				overall_loss += 1

		return {
			'overall_win': overall_win,
			'overall_loss': overall_loss,
			'remote_match_win': remote_match_win,
			'remote_match_loss': remote_match_loss,
			'ai_match_win': ai_match_win,
			'ai_match_loss': ai_match_loss,
		}
	
class UsersStatusListSerializer(serializers.ModelSerializer):
	user_status = serializers.SerializerMethodField()

	class Meta:
		model = CustomUser
		fields = ['id', 'username', 'user_status']

	def get_user(self, obj):
		return CustomUser.objects.get(id=obj.id)

	def get_user_status(self, obj):
		user = self.get_user(obj)
		if user.status_counter > 0:
			return "ON"
		return "OFF"