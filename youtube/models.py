from functools import reduce
from typing import List, Optional, Tuple, Union

from bellify_bot.models import Channel, ChannelUserItem, User
from django.conf import settings
from django.db import models
from django.db.models import Q
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

    @property
    def last_video(self: 'YouTubeChannel') -> str:
        return self.videos.all()[0]


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

    is_saved_livestream = models.BooleanField(default=False, **nb)
    is_notified = models.BooleanField(default=True, **nb)
    is_reuploaded = models.BooleanField(default=False, **nb)

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
    def tuple(self: 'YouTubeVideo') -> Tuple[str, str, bool]:
        return self.video_id, self.video_title, self.is_saved_livestream

    @classmethod
    def get_tuples_and_ids(cls, channel: Optional['YouTubeChannel'] = None):
        if channel:
            saved_videos_tuples = [
                video.tuple for video in channel.videos.all()]
            return saved_videos_tuples, [saved_video_tuple[0]
                                         for saved_video_tuple in saved_videos_tuples]
        else:
            saved_videos_tuples = [
                video.tuple for video in cls.objects.all()]
            return saved_videos_tuples, [saved_video_tuple[0]
                                         for saved_video_tuple in saved_videos_tuples]

    @classmethod
    def get_new_videos(cls, channel: 'YouTubeChannel', videos: Tuple[str, str, bool]) -> List['YouTubeVideo']:
        saved_videos_tuples = [video.tuple for video in channel.videos.all()]
        saved_videos_ids = [saved_video_tuple[0]
                            for saved_video_tuple in saved_videos_tuples]

        videos_ids = [video[0] for video in videos]

        if videos != saved_videos_tuples:
            channel.videos.all().delete()
            disable_notifications = False

            for video in videos:
                disable_notifications = video[0] in saved_videos_ids or disable_notifications
                YouTubeVideo.objects.get_or_create(
                    video_id=video[0],
                    video_title=video[1],
                    is_saved_livestream=video[2],
                    is_notified=disable_notifications,
                    is_reuploaded=YouTubeDeletedVideo.is_video_was_deleted(
                        channel, video[1]),
                    channel=channel
                )

            for saved_video_tuple in saved_videos_tuples:
                if not saved_video_tuple[0] in videos_ids:
                    YouTubeDeletedVideo.objects.get_or_create(
                        video_id=saved_video_tuple[0],
                        video_title=saved_video_tuple[1],
                        is_saved_livestream=saved_video_tuple[2],
                        channel=channel
                    )

        return channel.videos.all()

    def update(self: 'YouTubeVideo', video: Tuple[str, str, bool], is_notified: Optional[bool] = True, is_reuploaded: Optional[bool] = False):
        self.video_id, self.video_title, self.is_saved_livestream, self.is_notified, self.is_reuploaded = * \
            video, is_notified, is_reuploaded
        self.save()

    def notified(self: 'YouTubeVideo') -> None:
        self.is_notified = True
        self.is_reuploaded = False
        self.save()


# YouTube deleted video model
class YouTubeDeletedVideo(CreateUpdateTracker):
    video_id = models.CharField(max_length=20, **nb)
    video_title = models.CharField(max_length=256, **nb)
    is_saved_livestream = models.BooleanField(default=False, **nb)

    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE, related_name='deleted_videos', related_query_name='deleted_video')

    class Meta:
        verbose_name = 'Deleted YouTube Video'
        verbose_name_plural = 'Deleted YouTube Videos'

    def __str__(self):
        return f'{self.video_title}'

    @property
    def video_url(self: 'YouTubeVideo'):
        return f'https://www.youtube.com/watch?v={self.video_id}'

    @classmethod
    def is_video_was_deleted(cls, channel: YouTubeChannel, video_title: str) -> bool:
        return video_title in channel.deleted_videos.all()


# Custom through model with title
class YouTubeChannelUserItem(ChannelUserItem):
    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE)

    @ property
    def type(self: 'YouTubeChannelUserItem') -> str:
        return 'youtube'


@receiver(models.signals.post_save, sender=YouTubeVideo)
def remove_deleted_video_if_it_in_videos(sender: 'YouTubeVideo', instance, *args, **kwargs):
    _, videos_ids = sender.get_tuples_and_ids()
    queries = [Q(video_id__contains=video_id)
               for video_id in videos_ids]
    query = reduce(lambda x, y: x & y, queries)
    YouTubeDeletedVideo.objects.filter(query).delete()


@receiver(models.signals.post_delete, sender=YouTubeChannelUserItem)
def delete_channel_if_no_users_subscribed(sender, instance, *args, **kwargs):
    YouTubeChannel.objects.filter(
        youtubechanneluseritem__isnull=True).delete()
