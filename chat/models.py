from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('نام کاربری باید تنظیم شود')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)  # تنظیم رمز عبور
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True, verbose_name='نام کاربری')
    password = models.CharField(max_length=255, verbose_name='رمز عبور', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []  # حذف شماره تلفن

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return self.username

class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='joined_groups')  # تغییر نام
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    room_code = models.CharField(max_length=6, unique=True, verbose_name='کد روم')

    def __str__(self):
        return self.name

class Message(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'پیام'
        verbose_name_plural = 'پیام‌ها'

    def __str__(self):
        return f"[{self.group.name}] : {self.content[:30]}..."
