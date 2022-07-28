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

    saved_livestream_title = models.CharField(max_length=256, **nb)
    saved_livestream_url = models.URLField(**nb)
    saved_livestream_published = models.DateTimeField(
        default=datetime.date.min, **nb)

    iterations_skipped = models.PositiveSmallIntegerField(default=0)

    users = models.ManyToManyField(
        User, through='YouTubeChannelUserItem')

    class Meta:
        verbose_name = 'YouTube Channel'
        verbose_name_plural = 'YouTube Channels'

    def __str__(self):
        return f'{self.channel_title}'

    def iterations_skip(self, reset: Optional[bool] = False):
        if not reset:
            self.iterations_skipped = self.iterations_skipped + 1
        else:
            self.iterations_skipped = 0
        self.save()

    def update_live_info(self: 'YouTubeChannel', live_title: Optional[str] = None, live_url: Optional[str] = None, is_upcoming: Optional[bool] = None, is_live: Optional[bool] = False):
        self.live_title, self.live_url, self.is_upcoming, self.is_live = live_title, live_url, is_upcoming, is_live
        self.save()

    def update_video_info(self: 'YouTubeChannel', video_title: Optional[str] = None, video_url: Optional[str] = None, video_published: Optional[datetime.datetime] = None):
        self.video_title, self.video_url, self.video_published = video_title, video_url, video_published
        self.save()

    def update_saved_livestream_info(self: 'YouTubeChannel', saved_livestream_title: Optional[str] = None, saved_livestream_url: Optional[str] = None, saved_livestream_published: Optional[datetime.datetime] = None):
        self.saved_livestream_title, self.saved_livestream_url, self.saved_livestream_published = saved_livestream_title, saved_livestream_url, saved_livestream_published
        self.save()

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


@receiver(models.signals.post_delete, sender=YouTubeChannelUserItem)
def delete_channel_if_no_users_subscribed(sender, instance, *args, **kwargs):
    YouTubeChannel.objects.filter(youtubechanneluseritem__isnull=True).delete()
