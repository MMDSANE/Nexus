from rest_framework.permissions import BasePermission
from chat.models import RoomMembership


class IsRoomMember(BasePermission):

    def has_object_permission(self, request, view, obj):
        return RoomMembership.objects.filter(
            room=obj,
            user=request.user
        ).exists()