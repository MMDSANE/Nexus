# chat/urls.py

from django.urls import path
from .views import (
    create_room_view,
    join_room_view,
    chat_view,
    send_message_view,  # اضافه شد
    leave_chat_view,
    delete_room_view  # اضافه شد (اگرچه در تمپلیت استفاده نشد)
)

app_name = 'chat'

urlpatterns = [
    # 1. ایجاد روم
    path('create-room/', create_room_view, name='create_room'),

    # 2. صفحه اولیه برای ورود یا ساخت
    path('join-room/', join_room_view, name='join_room'),

    # 3. نمایش صفحه چت (هم برای تنظیم نام مهمان و هم نمایش چت پس از آن)
    path('room/<str:room_code>/', chat_view, name='chat_room'),

    # 4. ارسال پیام (باید POST باشد)
    path('room/<str:room_code>/send/', send_message_view, name='send_message'),

    # 5. خروج از روم (باید POST باشد)
    path('room/<str:room_code>/leave/', leave_chat_view, name='leave_chat'),

    # 6. حذف روم (باید POST باشد)
    path('room/<str:room_code>/delete/', delete_room_view, name='delete_room'),
]
