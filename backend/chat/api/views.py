from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from chat.services import create_room, join_room, leave_room
from .serializers import *
from chat.models import Message, RoomMembership
from .pagination import MessagePagination
from rest_framework.permissions import IsAuthenticated


class RoomCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RoomCreateSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        room = create_room(
            user=request.user,
            name=serializer.validated_data["name"]
        )

        return Response(RoomSerializer(room).data)


class RoomJoinView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RoomJoinSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            room = join_room(
                user=request.user,
                room_code=serializer.validated_data["room_code"]
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)

        return Response(RoomSerializer(room).data)


class RoomLeaveView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        result = leave_room(request.user, room_id)

        return Response({"status": result})


class MyRoomsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RoomSerializer

    def get_queryset(self):
        return Room.objects.filter(
            memberships__user=self.request.user
        ).distinct()

from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404



class RoomMessagesView(ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MessagePagination

    def get_room(self):
        return get_object_or_404(Room, id=self.kwargs["room_id"])

    def check_membership(self, room):
        is_member = RoomMembership.objects.filter(
            room=room,
            user=self.request.user
        ).exists()

        if not is_member:
            raise PermissionDenied("You are not a member of this room.")

    def get_queryset(self):
        room = self.get_room()
        self.check_membership(room)

        return (
            Message.objects
            .filter(room=room)
            .select_related("sender")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        room = self.get_room()
        self.check_membership(room)

        serializer.save(
            sender=self.request.user,
            room=room
        )