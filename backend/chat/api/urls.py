from django.urls import path
from .views import (
    RoomCreateView,
    RoomJoinView,
    RoomLeaveView,
    MyRoomsView,
    RoomMessagesView,
)

urlpatterns = [
    path("rooms/", RoomCreateView.as_view(), name="room-create"),
    path("rooms/join/", RoomJoinView.as_view(), name="room-join"),
    path("rooms/my/", MyRoomsView.as_view(), name="my-rooms"),
    path("rooms/<uuid:room_id>/leave/", RoomLeaveView.as_view(), name="room-leave"),

    # GET = history
    # POST = send message
    path(
        "rooms/<uuid:room_id>/messages/",
        RoomMessagesView.as_view(),
        name="room-messages",
    ),
]