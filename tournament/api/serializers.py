from rest_framework import serializers
from .models import CustomUser, Match, Friendship, Tournament, PlayerTournament
from django.db.models import Q



class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = '__all__' # returns all parameters
		extra_kwargs = {'password' : {'write_only': True}} # protects GET user/info/ from exposing the hash of the password in the response

	def create(self, validated_data):
		user = CustomUser.objects.create_user(**validated_data)
		return user
	
class MatchSerializer(serializers.ModelSerializer):
	#match = serializers.SerializerMethodField()
	class Meta:
		model = Match
		fields = '__all__' # returns all parameters

	def create(self, validated_data):
		match = Match.objects.create(**validated_data)
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
	
class TournamentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tournament
		fields = '__all__'
	
class PlayerTournamentSerializer(serializers.ModelSerializer):
	class Meta:
		model = PlayerTournament
		fields = '__all__'