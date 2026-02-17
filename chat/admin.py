# admin.py
from django.contrib import admin
from .models import User, Group, Message

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff')
    search_fields = ['username']

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ['name', 'room_code']

class MessageAdmin(admin.ModelAdmin):
    list_display = ('group', 'sender', 'content', 'timestamp')
    list_filter = ('group', 'sender')
    search_fields = ['content']

admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Message, MessageAdmin)
