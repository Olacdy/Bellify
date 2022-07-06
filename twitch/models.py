from django.core.files import File
from datetime import datetime, timedelta
from typing import Optional
from django.conf import settings
from bellify_bot.models import Channel, ChannelUserItem, User
from django.db import models
import urllib.request

from utils.models import nb


# Returns a path to the image
def twitch_thumbnail_directory_path(instance: 'TwitchChannel', filename: Optional[str] = ''):
    return f'twitch_thumbnails/{instance.channel_login}{settings.SPLITTING_CHARACTER}{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.jpg'


# TwitchChannel model
class TwitchChannel(Channel):
    channel_login = models.CharField(max_length=128)
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

    @property
    def type(self) -> str:
        return 'twitch'

    @classmethod
    def update_thumbnail_image(cls, channel: 'TwitchChannel', delete: Optional[bool] = False) -> None:
        if not delete:
            channel.thumbnail_image.save(
                twitch_thumbnail_directory_path(channel),
                File(open(urllib.request.urlretrieve(
                    channel.thumbnail_url)[0], 'rb')), save=False
            )
        else:
            channel.thumbnail_image.delete(save=False)

    @classmethod
    def update_live_info(cls, channel: 'TwitchChannel', live_title: Optional[str] = None, game_name: Optional[str] = None, thumbnail_url: Optional[str] = None, is_live: Optional[bool] = False) -> None:
        channel.live_title, channel.game_name, channel.thumbnail_url, channel.is_live = live_title, game_name, thumbnail_url, is_live


# Custom through model with title
class TwitchChannelUserItem(ChannelUserItem):
    channel = models.ForeignKey(
        TwitchChannel, on_delete=models.CASCADE)

    @property
    def type(self) -> str:
        return 'twitch'
