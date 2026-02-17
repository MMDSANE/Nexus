from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.core.cache import cache
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
import random, string, logging
from datetime import timedelta
from django.http import HttpResponse, JsonResponse  # JsonResponse برای پاسخ بهتر
from .constraints import *
from .models import *



# --- ویو ایجاد چت روم (فقط تولید کد و ریدایرکت) ---
def create_room_view(request):
    # تولید کد ۶ رقمی تصادفی
    room_code = ''.join(random.choices(string.digits, k=6))

    # ساخت روم در پایگاه داده
    Group.objects.create(room_code=room_code)

    # ریدایرکت به صفحه چت روم با کد تولید شده
    return redirect('chat:chat_room', room_code=room_code)




def join_room_view(request):
    if request.method == 'POST':
        room_code = request.POST.get('room_code')

        # اعتبارسنجی: آیا روم با این کد وجود دارد؟
        try:
            room = Group.objects.get(room_code=room_code)
            # اگر روم یافت شد، کاربر را به صفحه چت هدایت می‌کنیم
            return redirect('chat:chat_room', room_code=room_code)
        except Group.DoesNotExist:
            # در صورت عدم وجود، می‌توان یک پیغام خطا نمایش داد (فعلاً ساده‌سازی شده)
            context = {'error': 'کد روم یافت نشد.', 'room_code': room_code}
            return render(request, 'chat/join_form.html', context)  # نیاز به ساختن این فایل

    # اگر GET بود (اولین ورود به صفحه)
    return render(request, 'chat/join_form.html')




# --- تابع کمکی برای دریافت پیام‌ها (برای استفاده در chat_view) ---
def get_room_messages(room_code):
    try:
        room = Group.objects.get(room_code=room_code)
        # بازیابی 50 پیام آخر
        messages = Message.objects.filter(group=room).select_related('sender').order_by('timestamp')[:50]

        # تبدیل پیام‌ها به دیکشنری برای نمایش آسان‌تر در تمپلیت
        serialized_messages = []
        for msg in messages:
            # از آنجایی که در Guest ها User نداریم، باید وضعیت sender را چک کنیم
            sender_display = msg.sender.username if msg.sender else "Guest User (DB Error)"
            # تبدیل زمان به تایم زون ایران و اضافه کردن 3.5 ساعت
            msg_time = msg.timestamp + timedelta(hours=3.5)
            serialized_messages.append({
                'sender': sender_display,
                'content': msg.content,
                'timestamp': msg_time.strftime("%H:%M:%S"),
            })
        return serialized_messages
    except Group.DoesNotExist:
        return None




def chat_view(request, room_code):
    try:
        room = Group.objects.get(room_code=room_code)
    except Group.DoesNotExist:
        return render(request, "chat/chatroom_notfound.html")

    username = None
    is_authenticated = request.user.is_authenticated

    # --- 1. تعیین نام کاربری ---
    if is_authenticated:
        username = request.user.username
        # اگر کاربر لاگین شده است، نام او از پروفایل گرفته می‌شود.

    elif request.session.get(SESSION_CURRENT_ROOM_KEY) == room_code and SESSION_TEMP_USERNAME_KEY in request.session:
        # کاربر قبلاً به عنوان مهمان وارد شده است
        username = request.session.get(SESSION_TEMP_USERNAME_KEY)

    # --- 2. مدیریت فرم ارسال نام کاربری (مهمان جدید) ---
    if not username and request.method == 'POST' and 'username' in request.POST:
        submitted_username = request.POST.get('username', '').strip()

        if len(submitted_username) < 2:
            return render(request, 'chat/chat_room.html', {
                'room_code': room_code,
                'error': "نام کاربری باید حداقل ۲ کاراکتر باشد.",
                'get_username': True
            })

        # **تغییر اصلی: چک کردن وجود کاربر واقعی در دیتابیس برای جلوگیری از تداخل نام**
        if User.objects.filter(username=submitted_username).exists():
            return render(request, 'chat/chat_room.html', {
                'room_code': room_code,
                'error': "این نام کاربری توسط یک کاربر ثبت نام شده استفاده می‌شود. لطفاً نام دیگری انتخاب کنید.",
                'get_username': True
            })

        username = submitted_username
        request.session[SESSION_TEMP_USERNAME_KEY] = username
        request.session[SESSION_CURRENT_ROOM_KEY] = room_code

        # برای مهمان نیازی به login(request, request.user) نیست چون user.pk نداریم.

        return redirect('chat:chat_room', room_code=room_code)

    # --- 3. اگر هنوز نام کاربری مشخص نشده (اولین ورود) ---
    elif not username:
        return render(request, 'chat/chat_room.html', {
            'room_code': room_code,
            'get_username': True
        })

    # --- 4. مدیریت حضور (Presence) با کش ---

    cache_key = f"{CACHE_ROOM_PREFIX}{room_code}"

    # TTL (Time To Live) برای حضور مهمانان - مثلا 5 دقیقه
    PRESENCE_TIMEOUT = GUEST_PRESENCE_TIMEOUT

    if is_authenticated:
        # برای کاربر لاگین شده، حضور او با یوزنیم واقعی در کش ثبت می‌شود.
        # اگر نیاز به نگهداری اعضای روم در کش داریم:

        # برای این حالت، چون کاربر لاگین شده است، فرض می‌کنیم حضور او همیشه فعال است
        # مگر اینکه بخواهیم حضور لاگین شده ها را هم با TTL مدیریت کنیم (که معمولاً نمی‌کنند)

        # ما فقط نام کاربر لاگین شده را به لیست حاضرین اضافه می‌کنیم
        active_members_set = set(cache.get(cache_key, set()))
        active_members_set.add(username)

        # اگر کاربر لاگین شده است، اعضای روم را از کش خارج یا به‌روز نمی‌کنیم (یا با TTL بسیار طولانی)
        # اما اگر بخواهیم اعضای دیتابیس را هم ببینیم، باید مرحله 5 را تغییر دهیم.

    else:
        # کاربر مهمان (فقط در سشن و کش فعال است)

        # لیست کاربران فعال فعلی را از کش بگیرید (که باید از نوع set باشد)
        active_members_set = cache.get(cache_key, set())

        # نام مهمان را به لیست اضافه کرده و با TTL جدید به‌روز می‌کنیم
        active_members_set.add(username)

        # ذخیره مجدد لیست با TTL
        cache.set(cache_key, active_members_set, timeout=PRESENCE_TIMEOUT)

    # --- 5. نمایش اعضا و پیام‌ها ---

    room_messages = get_room_messages(room_code)

    all_active_users = set()

    # الف) کاربران لاگین شده (اعضای ثبت شده در دیتابیس روم)
    # اگر اتاق شما اعضای DB دارد، آن‌ها را اضافه می‌کنیم.
    if room.members.exists():
        # توجه: این کاربران همیشه حاضر فرض می‌شوند مگر اینکه از روم خارج شوند
        # یا منطق Presence پیچیده‌تری برای آن‌ها پیاده‌سازی شود.
        db_members = room.members.all().values_list('username', flat=True)
        all_active_users.update(db_members)

    # ب) کاربران فعال فعلی (مهمانان و لاگین شده‌هایی که در کش هستند)
    # ما از مقداری که در مرحله 4 محاسبه کردیم استفاده می‌کنیم.

    # اگر کاربر لاگین شده بود، username اضافه شد. اگر مهمان بود، نامش در کش ثبت و اینجا اضافه شد.
    current_presence = cache.get(cache_key, set())
    all_active_users.update(current_presence)

    # اگر کاربر لاگین شده بود و قبلاً در کش نبود (مثلا اولین بار وارد شده)
    if is_authenticated:
        all_active_users.add(username)

    context = {
        'room_code': room_code,
        'current_username': username,
        'is_logged_in': is_authenticated,
        'sender_identifier': username,
        'room_members_count': len(all_active_users),
        'active_guests_list': sorted(list(all_active_users)),
        'messages': room_messages,
        # دیگر نیازی به افزودن user به room.members.add(user) نیست
    }
    return render(request, 'chat/chat_room.html', context)




def send_message_view(request, room_code):
    # ۱. بررسی وجود روم
    try:
        room = Group.objects.get(room_code=room_code)
    except Group.DoesNotExist:
        return HttpResponse("Room not found.", status=404)

    content = request.POST.get('content', '').strip()
    if not content:
        return redirect('chat:chat_room', room_code=room_code)

    # ۲. تعیین فرستنده: اگر کاربر لاگین شده، از user استفاده کن
    # اگر نه، از temp_username در سشن استفاده کن (در صورت وجود)
    if request.user.is_authenticated:
        sender = request.user
    elif 'temp_username' in request.session and request.session['current_room_username'] == room_code:
        # اگر کاربر مهمان است، باید یک کاربر با این نام ایجاد شود
        try:
            sender = User.objects.get(username=request.session['temp_username'])
        except User.DoesNotExist:
            # اگر کاربر وجود ندارد، ایجادش کن
            sender = User.objects.create_user(username=request.session['temp_username'])
            login(request, sender)
    else:
        return HttpResponse("You must be logged in or have a temporary username.", status=403)

    # ۳. ذخیره پیام در دیتابیس
    Message.objects.create(
        group=room,
        sender=sender,
        content=content
    )

    # ۴. بازگشت به صفحه چت
    return redirect('chat:chat_room', room_code=room_code)


@require_POST
def leave_chat_view(request, room_code):
    try:
        room = Group.objects.get(room_code=room_code)
    except Group.DoesNotExist:
        return HttpResponse("Room not found.", status=404)

    is_authenticated = request.user.is_authenticated
    cache_key = f"{CACHE_ROOM_PREFIX}{room_code}"
    active_members_set = set(cache.get(cache_key, set()))

    UserClass = get_user_model()  # این مدل (chat.User)

    if is_authenticated:
        username_to_remove = request.user.username
        user_pk_to_delete = request.user.pk

        if username_to_remove in active_members_set:
            active_members_set.remove(username_to_remove)
            cache.set(cache_key, active_members_set, timeout=LOGGEDIN_PRESENCE_TIMEOUT)

        try:
            # 1. حذف پیام‌های کاربر در این روم
            Message.objects.filter(group=room, sender=UserClass.objects.get(pk=user_pk_to_delete)).delete()

            # 2. حذف عضویت در گروه
            if room.members.filter(pk=user_pk_to_delete).exists():
                room.members.remove(user_pk_to_delete)

            # 3. حذف کاربر از دیتابیس (این بار از مدل شما است)
            UserClass.objects.get(pk=user_pk_to_delete).delete()

        except UserClass.DoesNotExist:
            # کاربر قبلاً حذف شده
            pass
        except Exception as e:
            logging.info(f"Error during user cleanup: {e}")


    elif SESSION_TEMP_USERNAME_KEY in request.session:

        username_to_remove = request.session.get(SESSION_TEMP_USERNAME_KEY)

        if username_to_remove:

            # حذف از کش حضور

            cache_key = f"{CACHE_ROOM_PREFIX}{room_code}"

            active_members_set = cache.get(cache_key, set())

            if username_to_remove in active_members_set:
                active_members_set.remove(username_to_remove)

                cache.set(cache_key, active_members_set, timeout=GUEST_PRESENCE_TIMEOUT)

            # حذف نام کاربری از سشن

            del request.session[SESSION_TEMP_USERNAME_KEY]
            user_pk_to_delete = request.user.pk
            try:
                # 1. حذف پیام‌های کاربر در این روم
                Message.objects.filter(group=room, sender=UserClass.objects.get(pk=user_pk_to_delete)).delete()

                # 2. حذف عضویت در گروه
                if room.members.filter(pk=user_pk_to_delete).exists():
                    room.members.remove(user_pk_to_delete)

                # 3. حذف کاربر از دیتابیس (این بار از مدل شما است)
                UserClass.objects.get(pk=user_pk_to_delete).delete()

            except UserClass.DoesNotExist:
                # کاربر قبلاً حذف شده
                pass
            except Exception as e:
                logging.info(f"Error during user cleanup: {e}")

    # --- بررسی وضعیت نهایی روم ---
    logged_in_count = room.members.count()
    remaining_guests_set = cache.get(cache_key, set())
    remaining_guests_count = len(remaining_guests_set)
    total_active_count = logged_in_count + remaining_guests_count

    if total_active_count == 0:
        # حذف پیام‌های باقی‌مانده (مهمانان)
        Message.objects.filter(group=room).delete()
        room.delete()
        return render(request, "chat/chatroom_notfound.html")

    return render(request, "chat/logout_room.html")


# ویو برای حذف روم
@require_POST
def delete_room_view(request, room_code):
    try:
        room = Group.objects.get(room_code=room_code)

        # 1. حذف پیام‌ها
        Message.objects.filter(group=room).delete()

        # 2. حذف روم
        room.delete()

        # 3. پاکسازی کش مرتبط با این روم (برای تمیزی)
        cache_key = f"{CACHE_ROOM_PREFIX}{room_code}"
        cache.delete(cache_key)

        return HttpResponse("Room and messages deleted successfully.")
    except Group.DoesNotExist:
        return HttpResponse("Room not found.", status=404)
