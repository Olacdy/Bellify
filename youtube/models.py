from django.db import models
from bellify_bot.models import User, Channel, ChannelUserItem
from utils.models import nb


# YouTubeChannel model
class YouTubeChannel(Channel):
    video_title = models.CharField(max_length=256, **nb)
    video_url = models.URLField(**nb)

    old_video_title = models.CharField(max_length=256, **nb)
    old_video_url = models.URLField(**nb)

    live_url = models.URLField(**nb)

    users = models.ManyToManyField(
        User, through='YouTubeChannelUserItem')

    class Meta:
        verbose_name = 'YouTube Channel'
        verbose_name_plural = 'YouTube Channels'

    def __str__(self):
        return f'{self.channel_title}'

    @property
    def type(self) -> str:
        return 'youtube'


# Custom through model with title
class YouTubeChannelUserItem(ChannelUserItem):
    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE)

    @property
    def type(self) -> str:
        return 'youtube'
