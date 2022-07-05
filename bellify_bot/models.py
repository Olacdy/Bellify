from __future__ import annotations

from typing import Optional

from django.apps import apps
from django.conf import settings
from django.db import models
from django.db.models import Manager, Q, QuerySet
from utils.models import CreateUpdateTracker, GetOrNoneManager, nb

PLAN_CHOICES = (
    ('B', 'Basic'),
    ('P', 'Premium')
)

LANGUAGE_CHOICES = (
    ('en', 'English'),
    ('ru', 'Russian'),
    ('ua', 'Ukrainian')
)


class AdminUserManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_admin=True)


class User(CreateUpdateTracker):
    user_id = models.PositiveBigIntegerField(primary_key=True)
    username = models.CharField(max_length=64, **nb)
    first_name = models.CharField(max_length=256, **nb)
    last_name = models.CharField(max_length=256, **nb)
    deep_link = models.CharField(max_length=64, **nb)
    menu = models.CharField(max_length=64, **nb)

    status = models.CharField(
        max_length=1, choices=PLAN_CHOICES, default='B')

    language = models.CharField(
        max_length=2, choices=LANGUAGE_CHOICES, default=None, help_text="Telegram client's language", **nb)

    max_youtube_channels_number = models.PositiveIntegerField(
        default=settings.CHANNELS_INFO["youtube"]["initial_number"], **nb)
    max_twitch_channels_number = models.PositiveIntegerField(
        default=settings.CHANNELS_INFO["twitch"]["initial_number"], **nb)

    is_tutorial_finished = models.BooleanField(default=False)

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
    def get_max_for_channel(cls, u, channel_type: str) -> int:
        if 'YouTube' in channel_type:
            return u.max_youtube_channels_number
        elif 'Twitch' in channel_type:
            return u.max_twitch_channels_number

    @classmethod
    def set_menu_field(cls, u: User, value: Optional[str] = '') -> None:
        u = cls.objects.filter(user_id=u.user_id).first()
        u.menu = value
        u.save()

    @classmethod
    def set_language(cls, u: User, value: str) -> None:
        u = cls.objects.filter(user_id=u.user_id).first()
        u.language = value
        u.save()

    @classmethod
    def set_tutorial_state(cls, u: User, value: bool) -> None:
        u.is_tutorial_finished = value
        u.save()

    @classmethod
    def get_or_create_profile(cls, chat_id: str, username: str, reset: Optional[bool] = True):
        user_data = cls.objects.get_or_create(
            user_id=chat_id,
            defaults={
                'username': username,
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
        to='bellify_bot.User',
        verbose_name='User name',
        on_delete=models.CASCADE,
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


class ChannelUserItem(CreateUpdateTracker):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    channel_title = models.CharField(max_length=128, default='', **nb)
    is_muted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.channel_title

    @classmethod
    def is_user_subscribed_to_channel(cls, u: User, channel_id: str) -> bool:
        return cls.objects.filter(Q(user=u) & (Q(twitchchanneluseritem__channel__channel_id=channel_id) | Q(youtubechanneluseritem__channel__channel_id=channel_id))).exists()

    @classmethod
    def get_user_channel_by_id(cls, u: User, channel_id: str) -> 'ChannelUserItem':
        return cls.objects.filter(Q(user=u) & (Q(twitchchanneluseritem__channel__channel_id=channel_id) | Q(youtubechanneluseritem__channel__channel_id=channel_id))).first()

    @classmethod
    def get_count_by_user_and_channel(cls, u, channel_type: str) -> int:
        if 'YouTube' in channel_type:
            return apps.get_model('youtube', 'YouTubeChannelUserItem').objects.filter(user=u).count() + 1
        elif 'Twitch' in channel_type:
            return apps.get_model('twitch', 'TwitchChannelUserItem').objects.filter(user=u).count() + 1

    @classmethod
    def mute_channel(cls, u: User, channel: 'ChannelUserItem') -> None:
        channel.is_muted = not channel.is_muted
        channel.save()


class Channel(CreateUpdateTracker):
    channel_id = models.CharField(max_length=128, unique=True)
    channel_url = models.URLField(unique=True)
    channel_title = models.CharField(max_length=128)

    live_title = models.CharField(max_length=256, **nb)
    is_live = models.BooleanField(default=False, **nb)

    def __str__(self):
        return f'{self.channel_id}'
