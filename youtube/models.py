from datetime import datetime, timedelta
from re import L
from typing import Dict, List, Optional, Tuple, Union

from bellify_bot.models import Channel, ChannelUserItem, User
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.utils.timezone import now

from utils.models import CreateUpdateTracker, nb
from youtube.utils import get_url_from_id


# YouTube channel model
class YouTubeChannel(Channel):
    users = models.ManyToManyField(
        User, through='YouTubeChannelUserItem')

    deleted_livestreams = models.IntegerField(default=-1, **nb)

    class Meta:
        verbose_name = 'YouTube Channel'
        verbose_name_plural = 'YouTube Channels'

    def __str__(self):
        return f'{self.channel_title}'

    @property
    def type(self: 'YouTubeChannel') -> str:
        return 'youtube'

    @property
    def channel_url(self: 'Channel'):
        return get_url_from_id(self.channel_id)

    @property
    def last_video(self: 'YouTubeChannel') -> Union['YouTubeVideo', None]:
        video = self.videos.all().order_by('-added_at').first()
        return video if video else None

    @property
    def ongoing_livestream(self: 'YouTubeChannel') -> Union['YouTubeLivestream', None]:
        livestream = self.livestreams.filter(ended_at=None).first()
        return livestream if livestream else None

    @property
    def is_livestreaming(self: 'YouTubeChannel') -> bool:
        return bool(self.ongoing_livestream)

    @property
    def is_deleted_its_livestreams(self: 'YouTubeChannel') -> bool:
        return self.deleted_livestreams > 0

    @property
    def is_deleting_livestreams(self: 'YouTubeChannel') -> bool:
        return self.deleted_livestreams != 0

    @classmethod
    def get_channels_to_review(cls) -> List['YouTubeChannel']:
        return list(cls.objects.filter(youtubechanneluseritem__isnull=False).distinct())

    @classmethod
    def get_channels_to_review_premium(cls) -> List['YouTubeChannel']:
        return list(cls.objects.filter(Q(youtubechanneluseritem__isnull=False, users__status='P') | Q(livestream__isnull=False)).distinct())

    @classmethod
    def is_channel_exists(cls, channel_id: str) -> bool:
        return cls.objects.filter(channel_id=channel_id, youtubechanneluseritem__isnull=False).exists()

    def increment_deleted_livestreams(self: 'YouTubeChannel') -> None:
        if self.deleted_livestreams != -1:
            self.deleted_livestreams = self.deleted_livestreams + 1
        else:
            self.deleted_livestreams = 1
        self.save()

    def decrement_deleted_livestreams(self: 'YouTubeChannel') -> None:
        self.deleted_livestreams = self.deleted_livestreams - 1
        if self.deleted_livestreams < 0:
            self.deleted_livestreams = 0
        self.save()

    def clear_videos(self: 'YouTubeChannel') -> None:
        self.videos.all().delete()

    def clear_livestreams(self: 'YouTubeChannel') -> None:
        self.livestreams.all().delete()

    def clear_content(self: 'YouTubeChannel') -> None:
        self.clear_videos()
        self.clear_livestreams()
        self.deleted_livestreams = -1


# YouTube livestream model
class YouTubeLivestream(CreateUpdateTracker):
    livestream_id = models.CharField(max_length=20, **nb)
    livestream_title = models.CharField(max_length=256, **nb)

    is_notified = models.BooleanField(default=True, **nb)

    ended_at = models.DateTimeField(default=None, **nb)

    is_checked_for_deleted = models.BooleanField(default=False, **nb)

    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE, related_name='livestreams', related_query_name='livestream')

    class Meta:
        verbose_name = 'YouTube Livestream'
        verbose_name_plural = 'YouTube Livestreams'

    def __str__(self: 'YouTubeLivestream'):
        return f'{self.livestream_title}'

    @property
    def livestream_url(self: 'YouTubeLivestream') -> str:
        return f'https://www.youtube.com/watch?v={self.livestream_id}'

    @classmethod
    def get_livestreams_data(cls, channel: Optional[YouTubeChannel] = None) -> Dict[str, str]:
        return {livestream.livestream_id: livestream for livestream in (channel.livestreams.all() if channel else cls.objects.all())}

    @classmethod
    def get_new_livestreams(cls, channel: YouTubeChannel, livestreams: Dict[str, str]) -> List['YouTubeLivestream']:
        saved_livestreams = cls.get_livestreams_data(channel)

        livestreams_to_create = []

        for livestream_id in livestreams:
            if not cls.objects.filter(livestream_id=livestream_id).exists():
                livestreams_to_create.append(
                    YouTubeLivestream(
                        livestream_id=livestream_id,
                        livestream_title=livestreams[livestream_id],
                        is_notified=False,
                        channel=channel
                    )
                )

        for saved_livestream_id in saved_livestreams:
            if not saved_livestream_id in list(livestreams.keys()):
                if not saved_livestreams[saved_livestream_id].ended_at:
                    saved_livestreams[saved_livestream_id].set_ended()

        YouTubeLivestream.objects.bulk_create(livestreams_to_create)

        return channel.livestreams.all()

    @classmethod
    def is_ended_livestream(cls, channel: YouTubeChannel, video: Union['YouTubeVideo', Tuple[str, str]]) -> bool:
        if isinstance(video, YouTubeChannel):
            return channel.livestreams.filter(livestream_id=video.video_id, livestream_title=video.video_title).exists()
        elif isinstance(video, tuple):
            return channel.livestreams.filter(livestream_id=video[0], livestream_title=video[1]).exists()

    def set_notified(self: 'YouTubeLivestream') -> None:
        self.is_notified = True
        self.save()

    def set_checked(self: 'YouTubeLivestream') -> None:
        self.is_checked_for_deleted = True
        self.save()

    def set_ended(self: 'YouTubeLivestream') -> None:
        self.ended_at = now()
        self.save()


# YouTube video model
class YouTubeVideo(CreateUpdateTracker):
    video_id = models.CharField(max_length=20, **nb)
    video_title = models.CharField(max_length=256, **nb)
    is_saved_livestream = models.BooleanField(default=False, **nb)

    is_reuploaded = models.BooleanField(default=False, **nb)

    added_at = models.DateTimeField(default=now)
    published_at = models.DateTimeField(default=now)

    is_basic_notified = models.BooleanField(default=True, **nb)
    is_premium_notified = models.BooleanField(default=True, **nb)

    iterations_skipped = models.PositiveSmallIntegerField(default=0, **nb)

    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE, related_name='videos', related_query_name='video')

    class Meta:
        verbose_name = 'YouTube Video'
        verbose_name_plural = 'YouTube Videos'

    def __str__(self: 'YouTubeVideo'):
        return f'{self.video_title}'

    @property
    def video_url(self: 'YouTubeVideo') -> str:
        return f'https://www.youtube.com/watch?v={self.video_id}'

    @property
    def is_able_to_notify(self: 'YouTubeVideo') -> bool:
        return self.iterations_skipped >= settings.ITERATIONS_TO_SKIP

    @classmethod
    def get_new_videos(cls, channel: 'YouTubeChannel', videos: Dict[str, Tuple[str, bool]]) -> List['YouTubeVideo']:
        def _add_video(channel: YouTubeChannel, video: Dict[str, Union[datetime, str, bool]], index: int, is_basic_notified: Optional[bool] = False, is_premium_notified: Optional[bool] = False, iterations_skipped: Optional[int] = 0) -> 'YouTubeVideo':
            return YouTubeVideo(
                added_at=now() - timedelta(seconds=index),
                video_id=video['video_id'],
                video_title=video['video_title'],
                published_at=video['published_at'],
                is_saved_livestream=video['is_saved_livestream'],
                is_reuploaded=video['is_reuploaded'],
                is_basic_notified=is_basic_notified,
                is_premium_notified=is_premium_notified,
                iterations_skipped=iterations_skipped,
                channel=channel
            )

        videos_to_create = []
        is_trully_new = True

        for index, video_id in enumerate(videos):
            is_notified, is_reuploaded = YouTubeVideo.is_video_notified_and_reuploaded(
                channel=channel, video=(video_id, videos[video_id][0]))

            is_saved_livestream = YouTubeLivestream.is_ended_livestream(
                channel=channel, video=(video_id, videos[video_id][0]))

            if is_notified:
                is_trully_new = False
                video: YouTubeVideo = YouTubeVideo.objects.filter(
                    video_id__exact=video_id).distinct().first()
                if is_saved_livestream:
                    if video.is_able_to_notify:
                        video.set_unnotified_premium()
                    elif video.iterations_skipped > 0:
                        video.skip_iteration()
            else:
                if is_saved_livestream:
                    if channel.is_deleting_livestreams:
                        videos_to_create.append(
                            _add_video(channel=channel,
                                       video={
                                           'video_id': video_id,
                                           'video_title': videos[video_id][0],
                                           'published_at': videos[video_id][1],
                                           'is_saved_livestream': True,
                                           'is_reuploaded': is_reuploaded,
                                       },
                                       index=index,
                                       is_premium_notified=True,
                                       iterations_skipped=1)
                        )
                    else:
                        videos_to_create.append(
                            _add_video(channel=channel,
                                       video={
                                           'video_id': video_id,
                                           'video_title': videos[video_id][0],
                                           'published_at': videos[video_id][1],
                                           'is_saved_livestream': True,
                                           'is_reuploaded': is_reuploaded
                                       },
                                       index=index)
                        )
                else:
                    is_should_be_notified = videos[video_id][1] + \
                        settings.YOUTUBE_TIME_THRESHOLD[is_trully_new] > now()
                    if is_reuploaded:
                        YouTubeVideo.objects.filter(video_title=videos[video_id][0]).update(video_id=video_id, is_reuploaded=is_reuploaded,
                                                                                            is_basic_notified=is_should_be_notified,
                                                                                            is_premium_notified=is_should_be_notified)
                    else:
                        videos_to_create.append(
                            _add_video(channel=channel,
                                       video={
                                           'video_id': video_id,
                                           'video_title': videos[video_id][0],
                                           'published_at': videos[video_id][1],
                                           'is_saved_livestream': False,
                                           'is_reuploaded': is_reuploaded
                                       },
                                       index=index,
                                       is_basic_notified=not is_should_be_notified,
                                       is_premium_notified=not is_should_be_notified)
                        )

        YouTubeVideo.objects.bulk_create(videos_to_create)
        return channel.videos.all()

    @classmethod
    def is_video_notified(cls, channel: YouTubeChannel, video_id: str) -> bool:
        return cls.objects.filter(
            channel=channel, video_id__exact=video_id).exists()

    @classmethod
    def is_video_reuploaded(cls, channel: YouTubeChannel, video: Tuple[str, str]) -> bool:
        return cls.objects.filter(~Q(video_id__exact=video[0]) & Q(
            channel=channel, video_title__exact=video[1])).exists()

    @classmethod
    def is_video_notified_and_reuploaded(cls, channel: YouTubeChannel, video: Tuple[str, str]) -> Tuple[bool, bool]:
        return cls.is_video_notified(channel=channel, video_id=video[0]), cls.is_video_reuploaded(channel=channel, video=video)

    @classmethod
    def update_id_of_reuploaded_video(cls, channel: YouTubeChannel, video: Tuple[str, str]) -> None:
        reuploaded_videos = cls.objects.filter(
            channel=channel, video_title__exact=video[1])
        for reuploaded_video in reuploaded_videos:
            reuploaded_video.video_id = video[0]
            reuploaded_video.save()

    def skip_iteration(self: 'YouTubeVideo') -> None:
        self.iterations_skipped = self.iterations_skipped + 1
        self.save()

    def reset_iterations(self: 'YouTubeVideo') -> None:
        self.iterations_skipped = 0
        self.save()

    def set_notified_premium(self: 'YouTubeVideo') -> None:
        self.is_premium_notified = True
        self.iterations_skipped = 0
        if self.is_saved_livestream:
            self.channel.decrement_deleted_livestreams()
        self.save()

    def set_unnotified_premium(self: 'YouTubeVideo') -> None:
        self.is_premium_notified = False
        self.save()

    def set_notified_basic(self: 'YouTubeVideo') -> None:
        self.is_basic_notified = True
        self.save()

    def set_unnotified_basic(self: 'YouTubeVideo') -> None:
        self.is_basic_notified = False
        self.save()

    def set_title(self: 'YouTubeVideo', video_title: str) -> None:
        self.video_title = video_title
        self.save()


# Custom through model with title
class YouTubeChannelUserItem(ChannelUserItem):
    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE)

    @ property
    def type(self: 'YouTubeChannelUserItem') -> str:
        return 'youtube'


@receiver(models.signals.post_save, sender=YouTubeLivestream)
def remove_ended_livestreams_after_time(sender, instance, *args, **kwargs):
    for livestream in YouTubeLivestream.objects.all():
        if (now() - livestream.created_at).total_seconds() >= 86400 and livestream.ended_at:
            livestream.delete()


@receiver(models.signals.post_delete, sender=YouTubeChannelUserItem)
def clear_channels_content_if_no_subscribers(sender, instance, *args, **kwargs):
    for channel in YouTubeChannel.objects.filter(youtubechanneluseritem__isnull=True).distinct():
        channel.clear_content()

    for channel in YouTubeChannel.objects.filter(~Q(youtubechanneluseritem__user__status='P')).distinct():
        channel.clear_livestreams()
