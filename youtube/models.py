import datetime
from typing import Optional, Union

from bellify_bot.models import Channel, ChannelUserItem, User
from django.conf import settings
from django.db import models
from django.dispatch import receiver

from utils.models import CreateUpdateTracker, nb


# YouTube channel model
class YouTubeChannel(Channel):
    users = models.ManyToManyField(
        User, through='YouTubeChannelUserItem')

    class Meta:
        verbose_name = 'YouTube Channel'
        verbose_name_plural = 'YouTube Channels'

    def __str__(self):
        return f'{self.channel_title}'

    @property
    def type(self: 'YouTubeChannel') -> str:
        return 'youtube'


# YouTube livestream model
class YouTubeLivestream(CreateUpdateTracker):
    livestream_id = models.CharField(max_length=20, **nb)
    livestream_title = models.CharField(max_length=256, **nb)

    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE, related_name='livestreams', related_query_name='livestream')

    class Meta:
        verbose_name = 'YouTube Livestream'
        verbose_name_plural = 'YouTube Livestreams'

    def __str__(self):
        return f'{self.livestream_title}'

    def update(self: 'YouTubeLivestream', livestream_id: Optional[str] = None, livestream_title: Optional[str] = None, is_live: Optional[bool] = False, is_upcoming: Optional[bool] = False):
        self.livestream_id, self.livestream_title, self.is_live, self.is_upcoming = livestream_id, livestream_title, is_live, is_upcoming
        self.save()

    @classmethod
    def get_ongoing_livestream(cls, channel: YouTubeChannel) -> Union['YouTubeLivestream', bool]:
        livestreams = channel.livestreams.all()
        return livestreams[0] if livestreams else False

    @property
    def livestream_url(self: 'YouTubeLivestream'):
        return f'https://www.youtube.com/watch?v={self.livestream_id}'


# YouTube video model
class YouTubeVideo(CreateUpdateTracker):
    video_id = models.CharField(max_length=20, **nb)
    video_title = models.CharField(max_length=256, **nb)
    video_published = models.DateTimeField(default=datetime.datetime.strptime(
        '0001-01-01T00:00:00+00:00', '%Y-%m-%dT%H:%M:%S%z'), **nb)

    is_saved_livestream = models.BooleanField(default=False, **nb)

    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE, related_name='videos', related_query_name='video')

    class Meta:
        verbose_name = 'YouTube Video'
        verbose_name_plural = 'YouTube Videos'

    def __str__(self):
        return f'{self.video_title}'

    def update(self: 'YouTubeVideo', video_id: Optional[str] = None, video_title: Optional[str] = None, video_published: Optional[datetime.datetime] = None, is_saved_livestream: Optional[bool] = False):
        self.video_id, self.video_title, self.video_published, self.is_saved_livestream = video_id, video_title, video_published, is_saved_livestream
        self.save()

    @classmethod
    def get_last_video(cls, channel: YouTubeChannel) -> 'YouTubeVideo':
        return channel.videos.all()[0]

    @property
    def video_url(self: 'YouTubeVideo'):
        return f'https://www.youtube.com/watch?v={self.video_id}'


# Custom through model with title
class YouTubeChannelUserItem(ChannelUserItem):
    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE)

    @property
    def type(self: 'YouTubeChannelUserItem') -> str:
        return 'youtube'


@receiver(models.signals.post_delete, sender=YouTubeChannelUserItem)
def delete_channel_if_no_users_subscribed(sender, instance, *args, **kwargs):
    YouTubeChannel.objects.filter(youtubechanneluseritem__isnull=True).delete()
