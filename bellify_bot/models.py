from __future__ import annotations

from typing import Optional

from django.apps import apps
from django.conf import settings
from django.db import models
from django.db.models import Manager, Q, QuerySet
from telegram import User as TgUser
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
        max_length=2, choices=LANGUAGE_CHOICES, default=None, help_text='Telegram client\'s language', **nb)

    max_youtube_channels_number = models.PositiveIntegerField(verbose_name='YouTube Quota',
                                                              default=settings.CHANNELS_INFO['youtube']['initial_number'], **nb)
    max_twitch_channels_number = models.PositiveIntegerField(verbose_name='Twitch Quota',
                                                             default=settings.CHANNELS_INFO['twitch']['initial_number'], **nb)

    is_tutorial_finished = models.BooleanField(default=False)
    is_message_icons_disabled = models.BooleanField(default=False)
    is_manage_icons_disabled = models.BooleanField(default=False)
    is_twitch_thumbnail_disabled = models.BooleanField(default=False)

    is_blocked_bot = models.BooleanField(default=False)

    is_admin = models.BooleanField(default=False)

    objects = GetOrNoneManager()
    admins = AdminUserManager()

    class Meta:
        verbose_name = 'Telegram User'
        verbose_name_plural = 'Telegram Users'

    def __str__(self):
        return f'@{self.username}' if self.username is not None else f'{self.user_id}'

    @property
    def invited_users(self) -> QuerySet[User]:
        return User.objects.filter(deep_link=str(self.user_id), created_at__gt=self.created_at)

    @property
    def tg_str(self) -> str:
        if self.username:
            return self.username
        elif self.last_name and self.first_name:
            return f'{self.first_name} {self.last_name}'
        elif self.last_name:
            return self.last_name
        else:
            return self.user_id

    @classmethod
    def get_or_create_profile(cls, chat_id: str, tg_user: TgUser, reset: Optional[bool] = True):
        user_data = cls.objects.get_or_create(
            user_id=chat_id,
            defaults={
                'username': tg_user.username,
                'first_name': tg_user.first_name,
                'last_name': tg_user.last_name
            }
        )
        if user_data[0].username == settings.BOT_NAME:
            user_data[0].username = tg_user.username
            user_data[0].first_name = tg_user.first_name
            user_data[0].last_name = tg_user.last_name
            user_data[0].save()
        if reset:
            user_data[0].set_menu_field()
        return user_data

    def get_max_for_channel(self: User, channel_type: str) -> int:
        if 'YouTube' in channel_type:
            return self.max_youtube_channels_number
        elif 'Twitch' in channel_type:
            return self.max_twitch_channels_number

    def set_menu_field(self: User, value: Optional[str] = '') -> None:
        self.menu = value
        self.save()

    def set_language(self: User, value: str) -> None:
        self.language = value
        self.save()

    def set_message_icons_state(self: User) -> None:
        self.is_message_icons_disabled = not self.is_message_icons_disabled
        self.save()

    def set_manage_icons_state(self: User) -> None:
        self.is_manage_icons_disabled = not self.is_manage_icons_disabled
        self.save()

    def set_twitch_thumbnail_state(self: User) -> None:
        self.is_twitch_thumbnail_disabled = not self.is_twitch_thumbnail_disabled
        self.save()

    def set_tutorial_state(self: User, value: bool) -> None:
        self.is_tutorial_finished = value
        self.save()


class ChannelUserItem(CreateUpdateTracker):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    channel_title = models.CharField(max_length=128, default='', **nb)
    is_muted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.channel_title

    @property
    def manage_title_and_type(self) -> str:
        title = self.channel_title.replace(
            settings.CHANNELS_INFO[self.type]["icon"], "").strip()
        icon_or_none = f'{settings.CHANNELS_INFO[self.type]["icon"]} ' if not self.user.is_manage_icons_disabled else ''
        return f'{icon_or_none}{title}'

    @property
    def message_title_and_type(self) -> str:
        title = self.channel_title.replace(
            settings.CHANNELS_INFO[self.type]["icon"], "").strip()
        icon_or_none = f'{settings.CHANNELS_INFO[self.type]["icon"]} ' if not self.user.is_message_icons_disabled else ''
        return f'{icon_or_none}{title}'

    @classmethod
    def is_user_subscribed_to_channel(cls, user: User, channel_id: str) -> bool:
        return cls.objects.filter(Q(user=user) & (Q(twitchchanneluseritem__channel__channel_id=channel_id) | Q(youtubechanneluseritem__channel__channel_id=channel_id))).exists()

    @classmethod
    def get_channel_by_user_and_channel_id(cls, user: User, channel_id: str) -> 'ChannelUserItem':
        return cls.objects.filter(Q(user=user) & (Q(twitchchanneluseritem__channel__channel_id=channel_id) | Q(youtubechanneluseritem__channel__channel_id=channel_id))).first()

    @classmethod
    def get_count_by_user_and_channel(cls, user, channel_type: str) -> int:
        if 'YouTube' in channel_type:
            return apps.get_model('youtube', 'YouTubeChannelUserItem').objects.filter(user=user).count() + 1
        elif 'Twitch' in channel_type:
            return apps.get_model('twitch', 'TwitchChannelUserItem').objects.filter(user=user).count() + 1

    def mute_channel(self: 'ChannelUserItem') -> None:
        self.is_muted = not self.is_muted
        self.save()


class Channel(CreateUpdateTracker):
    channel_id = models.CharField(max_length=128, unique=True)
    channel_title = models.CharField(max_length=128)

    def __str__(self):
        return f'{self.channel_id}'

    @property
    def channel_url(self: 'Channel'):
        return ''
