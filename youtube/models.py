from django.db import models
from telegram_bot.models import User, Channel, ChannelUserItem
from utils.models import nb


# YouTubeChannel model
class YouTubeChannel(Channel):
    title = models.CharField(max_length=256)

    video_title = models.CharField(max_length=256, **nb)
    video_url = models.URLField(**nb)

    live_url = models.URLField(**nb)

    users = models.ManyToManyField(
        User, through='YouTubeChannelUserItem')

    class Meta:
        verbose_name = 'YouTube Channel'
        verbose_name_plural = 'YouTube Channels'

    def __str__(self):
        return f'{self.title}'


# Custom through model with title
class YouTubeChannelUserItem(ChannelUserItem):
    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE)
