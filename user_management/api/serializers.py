from rest_framework import serializers
from .models import CustomUser, Match, LocalMatch, AIMatch, Friendship
from django.db.models import Q
from django.db import models
from django.utils.translation import gettext_lazy



class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = '__all__' # returns all parameters
		extra_kwargs = {'password' : {'write_only': True}, 
						'two_factor_secret' : {'write_only' : True}} # protects GET user/info/ from exposing the hash of the password in the response

	def create(self, validated_data):
		user = CustomUser.objects.create_user(**validated_data)
		return user

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

class MatchHistorySerializer(serializers.ModelSerializer):
	player1_name = serializers.SerializerMethodField()
	player2_name = serializers.SerializerMethodField()
	date = serializers.DateTimeField(source='time_created')
	type = serializers.SerializerMethodField()

	class MatchTypes(models.TextChoices):
		MATCH = 'RM', gettext_lazy('Match')
		LOCAL_MATCH = 'LM', gettext_lazy('LocalMatch')
		AI_MATCH = 'AIM', gettext_lazy('AIMatch')

	class Meta:
		model = Match  # Use Match as a base model
		fields = ['id', 'player1_name', 'player2_name', 'player1_score', 'player2_score', 'date', 'type']

	def get_player1_name(self, obj):
		if isinstance(obj, Match):
			return obj.player1.username if obj.player1 else 'Unknown'
		elif isinstance(obj, LocalMatch):
			return obj.player1_tmp_username if obj.player1_tmp_username else 'Unknown'
		elif isinstance(obj, AIMatch):
			return obj.creator.username if obj.creator else 'Unknown'
		return 'Unknown'

	def get_player2_name(self, obj):
		if isinstance(obj, Match):
			return obj.player2.username if obj.player2 else 'Unknown'
		elif isinstance(obj, LocalMatch):
			return obj.player2_tmp_username if obj.player2_tmp_username else 'Unknown'
		elif isinstance(obj, AIMatch):
			return 'AI'
		return 'Unknown'

	def get_type(self, obj):
		if isinstance(obj, Match):
			return self.MatchTypes.MATCH.label
		elif isinstance(obj, LocalMatch):
			return self.MatchTypes.LOCAL_MATCH.label
		elif isinstance(obj, AIMatch):
			return self.MatchTypes.AI_MATCH.label
		return 'Unknown'

	def to_representation(self, instance):
		representation = super().to_representation(instance)
		representation['type'] = self.get_type(instance)
		return representation

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