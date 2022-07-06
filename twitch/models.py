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

    def save(self, *args, **kwargs):
        if self.thumbnail_url and self.is_5_minutes_expired:
            self.thumbnail_image.save(
                twitch_thumbnail_directory_path(self),
                File(open(urllib.request.urlretrieve(
                    self.thumbnail_url)[0], 'rb')), save=False
            )
        elif not self.thumbnail_url:
            self.thumbnail_image.delete(save=False)
        super(TwitchChannel, self).save(*args, **kwargs)

    @property
    def type(self) -> str:
        return 'twitch'

    @property
    def is_5_minutes_expired(self):
        try:
            old_datetime = self.thumbnail_image.name.split(
                f'{settings.SPLITTING_CHARACTER}')[-1]
            return old_datetime + timedelta(minutes=5) < datetime.now()
        except:
            return True

    @classmethod
    def update_live_info(cls, channel: 'TwitchChannel', live_title: Optional[str] = None, game_name: Optional[str] = None, thumbnail_url: Optional[str] = None, is_live: Optional[bool] = False):
        channel.live_title, channel.game_name, channel.thumbnail_url, channel.is_live = live_title, game_name, thumbnail_url, is_live


# Custom through model with title
class TwitchChannelUserItem(ChannelUserItem):
    channel = models.ForeignKey(
        TwitchChannel, on_delete=models.CASCADE)

    @property
    def type(self) -> str:
        return 'twitch'
