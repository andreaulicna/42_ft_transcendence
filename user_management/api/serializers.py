from rest_framework import serializers
from .models import CustomUser, Match, Friendship


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
	
#class FriendshipSerializer(serializers.ModelSerializer):
#	sender_status = serializers.SerializerMethodField()
#	receiver_status = serializers.SerializerMethodField()
#
#	class Meta:
#		model = Friendship
#		fields = ['id', 'sender', 'receiver', 'status', 'sender_status', 'receiver_status']
#
#	def get_sender_status(self, obj):
#		user = CustomUser.objects.get(id=obj.sender.id)
#		if user.status_counter > 0:
#			return "online"
#		return "offline"
#
#	def get_receiver_status(self, obj):
#		user = CustomUser.objects.get(id=obj.receiver.id)
#		if user.status_counter > 0:
#			return "online"
#		return "offline"