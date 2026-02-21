# chat/models.py

import uuid
import random
import string
from django.db import models
from django.conf import settings


def generate_room_code():
    return ''.join(random.choices(string.digits, k=6))


class Room(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=120)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_rooms"
    )

    room_code = models.CharField(
        max_length=6,
        unique=True,
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.room_code:
            self.room_code = generate_room_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.room_code})"

class RoomMembership(models.Model):

    ROLE_CHOICES = (
        ("owner", "Owner"),
        ("member", "Member"),
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="room_memberships"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("room", "user")



class Message(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]