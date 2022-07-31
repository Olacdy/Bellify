from datetime import datetime
from typing import Optional

import requests
from bellify_bot.models import Channel, ChannelUserItem, User
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.dispatch import receiver

from utils.models import nb


# Returns a path to the image
def twitch_thumbnail_directory_path(instance: 'TwitchChannel', filename: Optional[str] = ''):
    return f'twitch_thumbnails/{instance.channel_login}-{datetime.now().strftime("%Y-%m-%dT%H.%M.%S")}.jpg'


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

    users = models.ManyToManyField(
        User, through='TwitchChannelUserItem')

    class Meta:
        verbose_name = 'Twitch Channel'
        verbose_name_plural = 'Twitch Channels'

    def __str__(self):
        return f'{self.channel_title}'

    def update_live_info(self: 'TwitchChannel', live_title: Optional[str] = None, game_name: Optional[str] = None, thumbnail_url: Optional[str] = None, is_live: Optional[bool] = False) -> None:
        self.live_title, self.game_name, self.thumbnail_url, self.is_live = live_title, game_name, thumbnail_url, is_live
        if thumbnail_url:
            self.thumbnail_image.save(
                twitch_thumbnail_directory_path(self), ContentFile(requests.get(thumbnail_url if thumbnail_url else self.thumbnail_url).content))
        else:
            self.thumbnail_image.delete()
        self.save()

    @classmethod
    def get_or_update_bearer_token(cls, update: Optional[bool] = False):
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

    @property
    def type(self) -> str:
        return 'twitch'

    @property
    def thumbnail(self) -> str:
        if self.thumbnail_url:
            try:
                return f'{settings.ABSOLUTE_URL}{self.thumbnail_image.url}'
            except:
                return self.thumbnail_url
        else:
            return ''

    @property
    def preview_url(self) -> str:
        return f'{settings.ABSOLUTE_URL}/{self.type}/{self.channel_login}/{datetime.now().strftime("%Y-%m-%dT%H.%M.%S")}'


# Custom through model with title
class TwitchChannelUserItem(ChannelUserItem):
    channel = models.ForeignKey(
        TwitchChannel, on_delete=models.CASCADE)

    @property
    def type(self) -> str:
        return 'twitch'


@receiver(models.signals.post_delete, sender=TwitchChannelUserItem)
def delete_channel_if_no_users_subscribed(sender, instance, *args, **kwargs):
    TwitchChannel.objects.filter(twitchchanneluseritem__isnull=True).delete()
