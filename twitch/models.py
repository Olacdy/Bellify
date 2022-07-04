from django.db import models
from bellify_bot.models import User, Channel, ChannelUserItem
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


# Custom through model with title
class TwitchChannelUserItem(ChannelUserItem):
    channel = models.ForeignKey(
        TwitchChannel, on_delete=models.CASCADE)

    @property
    def type(self) -> str:
        return 'twitch'
