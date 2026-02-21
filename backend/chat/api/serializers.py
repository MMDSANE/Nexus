from rest_framework import serializers
from chat.models import Room, Message


class RoomCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)


class RoomJoinSerializer(serializers.Serializer):
    room_code = serializers.CharField(max_length=6)


class RoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = Room
        fields = ["id", "name", "room_code", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.UUIDField(source="sender.id", read_only=True)
    sender_username = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "content",
            "sender_id",
            "sender_username",
            "created_at",
        ]