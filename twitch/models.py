from django.db import models
from telegram_bot.models import User, Channel, ChannelUserItem
from utils.models import nb


# TwitchChannel model
class TwitchChannel(Channel):
    users = models.ManyToManyField(
        User, through='TwitchChannelUserItem')

    class Meta:
        verbose_name = 'Twitch Channel'
        verbose_name_plural = 'Twitch Channels'


# Custom through model with title
class TwitchChannelUserItem(ChannelUserItem):
    channel = models.ForeignKey(
        TwitchChannel, on_delete=models.CASCADE)
