from datetime import datetime, timedelta
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
    def is_10_minutes_expired(self):
        try:
            old_datetime = datetime.strptime(self.thumbnail_image.name.split(
                f'{settings.SPLITTING_CHARACTER}')[-1].replace('.jpg', ''), '%Y_%m_%d_%H_%M_%S')
            return old_datetime + timedelta(minutes=10) < datetime.now()
        except:
            return True

    @classmethod
    def update_thumbnail_image(cls, channel: 'TwitchChannel', thumbnail_url: Optional[str] = '', delete: Optional[bool] = False, save: Optional[bool] = False) -> None:
        if not delete:
            if channel.is_10_minutes_expired:
                channel.thumbnail_image.save(
                    twitch_thumbnail_directory_path(channel), ContentFile(requests.get(thumbnail_url if thumbnail_url else channel.thumbnail_url).content), save=save)
        else:
            channel.thumbnail_image.delete(save=save)

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

    @property
    def title_type(self) -> str:
        return f'{settings.CHANNELS_INFO[self.type]["icon"]} {self.channel_title.replace(settings.CHANNELS_INFO[self.type]["icon"], "").strip()}'


@receiver(models.signals.post_delete, sender=TwitchChannelUserItem)
def delete_channel_if_no_users_subscribed(sender, instance, *args, **kwargs):
    TwitchChannel.objects.filter(twitchchanneluseritem__isnull=True).delete()
