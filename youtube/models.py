import datetime
from typing import Optional

from bellify_bot.models import Channel, ChannelUserItem, User
from django.conf import settings
from django.db import models
from django.dispatch import receiver

from utils.models import nb


# YouTubeChannel model
class YouTubeChannel(Channel):
    video_title = models.CharField(max_length=256, **nb)
    video_url = models.URLField(**nb)

    video_published = models.DateTimeField(default=datetime.date.min, **nb)

    live_url = models.URLField(**nb)
    is_upcoming = models.BooleanField(**nb)

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

    @classmethod
    def update_live_info(cls, channel: 'YouTubeChannel', live_title: Optional[str] = None, live_url: Optional[str] = None, is_upcoming: Optional[bool] = None, is_live: Optional[bool] = False):
        channel.live_title, channel.live_url, channel.is_upcoming, channel.is_live = live_title, live_url, is_upcoming, is_live

    @classmethod
    def update_video_info(cls, channel: 'YouTubeChannel', video_title: Optional[str] = None, video_url: Optional[str] = None, video_published: Optional[datetime.datetime] = None):
        channel.video_title, channel.video_url, channel.video_published = video_title, video_url, video_published


# Custom through model with title
class YouTubeChannelUserItem(ChannelUserItem):
    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE)

    @property
    def type(self) -> str:
        return 'youtube'

    @property
    def title_type(self) -> str:
        return f'{settings.CHANNELS_INFO[self.type]["icon"] if not self.user.is_icons_disabled else ""} {self.channel_title.replace(settings.CHANNELS_INFO[self.type]["icon"], "").strip()}'.strip()


@receiver(models.signals.post_delete, sender=YouTubeChannelUserItem)
def delete_channel_if_no_users_subscribed(sender, instance, *args, **kwargs):
    YouTubeChannel.objects.filter(youtubechanneluseritem__isnull=True).delete()
