from __future__ import annotations
from django.db import models

from typing import Optional

from django.db import models
from django.db.models import QuerySet, Manager

from utils.models import CreateUpdateTracker, nb, GetOrNoneManager


class AdminUserManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_admin=True)


class User(CreateUpdateTracker):
    user_id = models.PositiveBigIntegerField(primary_key=True)
    username = models.CharField(max_length=64, **nb)
    first_name = models.CharField(max_length=256, **nb)
    last_name = models.CharField(max_length=256, **nb)
    language = models.CharField(
        max_length=8, help_text="Telegram client's lang", **nb)
    deep_link = models.CharField(max_length=64, **nb)
    menu = models.CharField(max_length=64, **nb)

    is_blocked_bot = models.BooleanField(default=False)

    is_admin = models.BooleanField(default=False)

    objects = GetOrNoneManager()
    admins = AdminUserManager()

    class Meta:
        verbose_name = 'Telegram User'
        verbose_name_plural = 'Telegram Users'

    def __str__(self):
        return f'@{self.username}' if self.username is not None else f'{self.user_id}'

    @classmethod
    def set_menu_field(cls, u: User, value: Optional[str] = '') -> None:
        u = cls.objects.filter(user_id=u.user_id).first()
        u.menu = value
        u.save()

    @classmethod
    def get_or_create_profile(cls, chat_id: str, username: str, reset: Optional[bool] = True):
        user_data = cls.objects.get_or_create(
            user_id=chat_id,
            defaults={
                'username': username,
                'language': 'en',
            }
        )
        if reset:
            User.set_menu_field(user_data[0])
        return user_data

    @property
    def invited_users(self) -> QuerySet[User]:
        return User.objects.filter(deep_link=str(self.user_id), created_at__gt=self.created_at)

    @property
    def tg_str(self) -> str:
        if self.username:
            return f'@{self.username}'
        return f"{self.first_name} {self.last_name}" if self.last_name else f"{self.first_name}"


class Message(CreateUpdateTracker):
    user = models.ForeignKey(
        to='telegram_bot.User',
        verbose_name='User name',
        on_delete=models.PROTECT,
    )
    text = models.TextField(
        verbose_name='Text',
    )

    def __str__(self):
        return f'Message {self.pk} of {self.user}'

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Message'

    @classmethod
    def get_or_create_message(cls, u: User, text: str):
        return cls.objects.get_or_create(
            text=text,
            user=u
        )
