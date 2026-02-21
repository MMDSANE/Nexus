import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from chat.models import Room, RoomMembership, Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope.get("user")
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        # اگر لاگین نباشد
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        # بررسی عضویت
        is_member = await self.is_room_member()

        if not is_member:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data.get("message")

        if not content:
            return

        # ذخیره پیام در دیتابیس
        message = await self.save_message(content)

        # ارسال به همه اعضای آنلاین
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message.content,
                "sender": str(self.user.id),
                "created_at": str(message.created_at),
            }
        )


    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "sender": event["sender"],
                    "created_at": event["created_at"],
                }
            )
        )


    # -------------------------
    # Database operations
    # -------------------------

    @database_sync_to_async
    def is_room_member(self):
        return RoomMembership.objects.filter(
            room_id=self.room_id,
            user=self.user
        ).exists()


    @database_sync_to_async
    def save_message(self, content):
        return Message.objects.create(
            room_id=self.room_id,
            sender=self.user,
            content=content
        )