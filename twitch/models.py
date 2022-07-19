from typing import Optional
from datetime import datetime
from bellify_bot.models import Channel, ChannelUserItem, User
from django.conf import settings
from django.db import models
from django.dispatch import receiver

from utils.models import nb


# TwitchChannel model
class TwitchChannel(Channel):
    channel_login = models.CharField(max_length=128)
    game_name = models.CharField(max_length=128, **nb)
    thumbnail_url = models.URLField(**nb)

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
    def preview_url(self) -> str:
        return f'{settings.ABSOLUTE_URL}/{self.type}/{self.channel_login}/{datetime.now()}'

    @property
    def video_url(self) -> str:
        return f'https://player.twitch.tv/?channel={self.channel_login}&player=facebook&autoplay=true&parent=meta.tag'

    @classmethod
    def update_live_info(cls, channel: 'TwitchChannel', live_title: Optional[str] = None, game_name: Optional[str] = None, thumbnail_url: Optional[str] = None, is_live: Optional[bool] = False) -> None:
        channel.live_title, channel.game_name, channel.thumbnail_url, channel.is_live = live_title, game_name, thumbnail_url, is_live
        channel.save()


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
