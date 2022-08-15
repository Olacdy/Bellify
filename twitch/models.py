from typing import Optional, List

import requests
from bellify_bot.models import Channel, ChannelUserItem, User
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.dispatch import receiver
from django.utils.timezone import now
from twitch.utils import get_url_from_title

from utils.models import nb


# Returns a path to the image
def twitch_thumbnail_directory_path(instance: 'TwitchChannel', filename: Optional[str] = ''):
    return f'twitch_thumbnails/{instance.channel_login}-{now().strftime("%Y-%m-%dT%H.%M.%S")}.jpg'


# Twitch channel model
class TwitchChannel(Channel):
    _bearer_token = ''

    channel_login = models.CharField(max_length=128)

    live_title = models.CharField(max_length=256, **nb)
    is_live = models.BooleanField(default=False, **nb)
    game_name = models.CharField(max_length=128, **nb)
    thumbnail_url = models.URLField(**nb)
    thumbnail_image = models.ImageField(
        upload_to=twitch_thumbnail_directory_path, **nb)

    live_end_datetime = models.DateTimeField(default=now, **nb)

    users = models.ManyToManyField(
        User, through='TwitchChannelUserItem')

    class Meta:
        verbose_name = 'Twitch Channel'
        verbose_name_plural = 'Twitch Channels'

    def __str__(self: 'TwitchChannel'):
        return f'{self.channel_title}'

    @property
    def type(self: 'TwitchChannel') -> str:
        return 'twitch'

    @property
    def channel_url(self: 'Channel'):
        return get_url_from_title(self.channel_title)

    @property
    def thumbnail(self: 'TwitchChannel') -> str:
        if self.thumbnail_url:
            try:
                return f'{settings.ABSOLUTE_URL}{self.thumbnail_image.url}'
            except:
                return self.thumbnail_url
        else:
            return ''

    @property
    def preview_url(self: 'TwitchChannel') -> str:
        return f'{settings.ABSOLUTE_URL}/{self.type}/{self.channel_login}/{now().strftime("%Y-%m-%dT%H.%M.%S")}'

    @property
    def is_threshold_passed(self: 'TwitchChannel') -> bool:
        return self.live_end_datetime + settings.TIME_THRESHOLD < now()

    @classmethod
    def get_channels_to_review(cls) -> List['TwitchChannel']:
        return list(cls.objects.filter(twitchchanneluseritem__isnull=False).distinct())

    @classmethod
    def is_channel_exists(cls, channel_id: str) -> bool:
        return cls.objects.filter(channel_id=channel_id, twitchchanneluseritem__isnull=False).exists()

    @classmethod
    def get_or_update_bearer_token(cls, update: Optional[bool] = False) -> str:
        if not cls._bearer_token or update:

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            params = {
                'client_id': settings.TWITCH_CLIENT_ID,
                'client_secret': settings.TWITCH_CLIENT_SECRET,
                'grant_type': 'client_credentials'
            }

            response = requests.post(
                'https://id.twitch.tv/oauth2/token', headers=headers, params=params)

            cls._bearer_token = response.json()['access_token']

        return cls._bearer_token

    def update(self: 'TwitchChannel', live_title: Optional[str] = None, game_name: Optional[str] = None, thumbnail_url: Optional[str] = None, is_live: Optional[bool] = False) -> None:
        self.live_title, self.game_name, self.thumbnail_url, self.is_live = live_title, game_name, thumbnail_url, is_live

        if not is_live:
            self.live_end_datetime = now()

        if thumbnail_url:
            self.thumbnail_image.save(
                twitch_thumbnail_directory_path(self), ContentFile(requests.get(thumbnail_url if thumbnail_url else self.thumbnail_url).content))
        else:
            self.thumbnail_image.delete()
        self.save()

    def clear_content(self: 'TwitchChannel'):
        self.update()


# Custom through model with title
class TwitchChannelUserItem(ChannelUserItem):
    channel = models.ForeignKey(
        TwitchChannel, on_delete=models.CASCADE)

    @property
    def type(self) -> str:
        return 'twitch'


@receiver(models.signals.post_delete, sender=TwitchChannelUserItem)
def clear_channels_content_if_no_subscribers(sender, instance, *args, **kwargs):
    for channel in TwitchChannel.objects.filter(twitchchanneluseritem__isnull=True).distinct():
        channel.clear_content()
