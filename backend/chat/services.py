from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Room, RoomMembership


@transaction.atomic
def create_room(user, name):
    room = Room.objects.create(
        name=name,
        owner=user,
    )

    RoomMembership.objects.create(
        room=room,
        user=user,
        role="owner"
    )

    return room


@transaction.atomic
def join_room(user, room_code):
    room = get_object_or_404(Room, room_code=room_code)

    if RoomMembership.objects.filter(room=room, user=user).exists():
        raise ValueError("Already a member")

    RoomMembership.objects.create(
        room=room,
        user=user,
        role="member"
    )

    return room


@transaction.atomic
def leave_room(user, room_id):
    room = get_object_or_404(Room, id=room_id)
    membership = get_object_or_404(RoomMembership, room=room, user=user)

    if membership.role == "owner":
        room.delete()
        return "room_deleted"

    membership.delete()
    return "left"