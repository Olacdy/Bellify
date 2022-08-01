import datetime
from typing import Optional, Union, Tuple, List

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

    @property
    def livestream_url(self: 'YouTubeLivestream'):
        return f'https://www.youtube.com/watch?v={self.livestream_id}'

    @classmethod
    def get_ongoing_livestream(cls, channel: YouTubeChannel) -> Union['YouTubeLivestream', bool]:
        livestreams = channel.livestreams.all()
        return livestreams[0] if livestreams else False

    def update(self: 'YouTubeLivestream', livestream_id: Optional[str] = None, livestream_title: Optional[str] = None, is_live: Optional[bool] = False, is_upcoming: Optional[bool] = False):
        self.livestream_id, self.livestream_title, self.is_live, self.is_upcoming = livestream_id, livestream_title, is_live, is_upcoming
        self.save()


# YouTube video model
class YouTubeVideo(CreateUpdateTracker):
    video_id = models.CharField(max_length=20, **nb)
    video_title = models.CharField(max_length=256, **nb)
    video_published = models.DateTimeField(default=datetime.datetime.strptime(
        '0001-01-01T00:00:00+00:00', '%Y-%m-%dT%H:%M:%S%z'), **nb)

    is_saved_livestream = models.BooleanField(default=False, **nb)
    is_notified = models.BooleanField(default=True, **nb)

    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE, related_name='videos', related_query_name='video')

    class Meta:
        verbose_name = 'YouTube Video'
        verbose_name_plural = 'YouTube Videos'

    def __str__(self):
        return f'{self.video_title}'

    @property
    def video_url(self: 'YouTubeVideo'):
        return f'https://www.youtube.com/watch?v={self.video_id}'

    @property
    def tuple(self: 'YouTubeVideo') -> Tuple[str, str]:
        return self.video_id, self.video_title

    @classmethod
    def add_new_videos(cls, channel: YouTubeChannel, videos: List[Tuple[str, str, str, bool]]) -> List['YouTubeVideo']:
        videos_info = {}
        only_notified = False

        channel_videos = list(channel.videos.all())
        channel_videos_tuple = YouTubeVideo.get_tuples(channel_videos)
        for video in videos:
            only_notified = video[0:2] in channel_videos_tuple or only_notified
            videos_info.append(
                (video, video[0:2] in channel_videos_tuple or only_notified))

        for i, video_info in enumerate(videos_info):
            video, is_notified = video_info
            try:
                channel_videos[i].update(video, is_notified)
            except IndexError:
                YouTubeVideo.objects.update_or_create(
                    video_id=video[0],
                    video_title=video[1],
                    video_published=video[2],
                    is_saved_livestream=video[3],
                    channel=channel
                )

        return channel_videos

    @classmethod
    def get_last_video(cls, channel: YouTubeChannel) -> 'YouTubeVideo':
        return channel.videos.all()[0]

    @classmethod
    def get_tuples(cls, videos: List['YouTubeVideo']) -> List[Tuple[str, str]]:
        return [(video.video_id, video.video_title) for video in videos]

    def update(self: 'YouTubeVideo', video_info: List[Tuple[str, str, str, bool]], is_notified: Optional[bool] = False):
        self.video_id, self.video_title, self.video_published, self.is_saved_livestream, self.is_notified = * \
            video_info, is_notified
        self.save()

    def notified(self: 'YouTubeVideo') -> None:
        self.is_notified = True
        self.save()


# Custom through model with title
class YouTubeChannelUserItem(ChannelUserItem):
    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE)

    @ property
    def type(self: 'YouTubeChannelUserItem') -> str:
        return 'youtube'


@ receiver(models.signals.post_delete, sender=YouTubeChannelUserItem)
def delete_channel_if_no_users_subscribed(sender, instance, *args, **kwargs):
    YouTubeChannel.objects.filter(
        youtubechanneluseritem__isnull=True).delete()
