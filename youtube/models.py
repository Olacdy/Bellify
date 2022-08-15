from functools import reduce
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
        video = self.videos.all().first()
        return video if video else None

    @property
    def ongoing_livestream(self: 'YouTubeChannel') -> Union['YouTubeLivestream', bool]:
        livestream = self.livestreams.all().first()
        return livestream if livestream else False

    @property
    def is_livestreaming(self: 'YouTubeChannel') -> bool:
        return bool(self.ongoing_livestream)

    @property
    def check_for_deleting_livestreams(self: 'YouTubeChannel') -> bool:
        return self.deleted_livestreams != 0

    @property
    def is_deleting_livestreams(self: 'YouTubeChannel') -> bool:
        return self.deleted_livestreams > 0

    @classmethod
    def get_channels_to_review(cls) -> List['YouTubeChannel']:
        return list(cls.objects.filter(youtubechanneluseritem__isnull=False).distinct())

    @classmethod
    def get_channels_to_review_premium(cls) -> List['YouTubeChannel']:
        return list(cls.objects.filter(youtubechanneluseritem__isnull=False, users__status='P').distinct())

    @classmethod
    def is_channel_exists(cls, channel_id: str) -> bool:
        return cls.objects.filter(channel_id=channel_id, youtubechanneluseritem__isnull=False).exists()

    def set_not_new_if_all_videos_are_new(self: 'YouTubeChannel') -> None:
        if self.videos.filter(is_new=True).count() == self.videos.count() and self.videos.count() > 1:
            self.videos.update(is_new=False)

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


# Parent of YouTubeLivestream models
class YouTubeLivestreamParent(CreateUpdateTracker):
    livestream_id = models.CharField(max_length=20, **nb)
    livestream_title = models.CharField(max_length=256, **nb)

    class Meta:
        abstract = True

    def __str__(self: 'YouTubeLivestreamParent'):
        return f'{self.livestream_title}'

    @property
    def livestream_url(self: 'YouTubeLivestreamParent') -> str:
        return f'https://www.youtube.com/watch?v={self.livestream_id}'


# YouTube livestream model
class YouTubeLivestream(YouTubeLivestreamParent):
    is_new = models.BooleanField(default=False, **nb)

    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE, related_name='livestreams', related_query_name='livestream')

    class Meta:
        verbose_name = 'YouTube Livestream'
        verbose_name_plural = 'YouTube Livestreams'

    @classmethod
    def get_livestreams_data(cls, channel: Optional[YouTubeChannel] = None) -> Dict[str, str]:
        return {livestream.livestream_id: livestream.livestream_title for livestream in (channel.livestreams.all() if channel else cls.objects.all())}

    @classmethod
    def get_new_livestreams(cls, channel: YouTubeChannel, livestreams: Dict[str, str]) -> List['YouTubeLivestream']:
        saved_livestreams = cls.get_livestreams_data(channel)

        if livestreams.keys() != saved_livestreams.keys():
            channel.clear_livestreams()
            livestreams_to_create = []
            ended_livestreams_to_create = []

            for livestream_id in livestreams:
                livestreams_to_create.append(
                    YouTubeLivestream(
                        livestream_id=livestream_id,
                        livestream_title=livestreams[livestream_id],
                        is_new=not livestream_id in saved_livestreams,
                        channel=channel
                    )
                )

            for saved_livestream_id in saved_livestreams:
                if not saved_livestream_id in livestreams:
                    ended_livestreams_to_create.append(
                        YouTubeEndedLivestream(
                            livestream_id=saved_livestream_id,
                            livestream_title=saved_livestreams[saved_livestream_id],
                            channel=channel
                        )
                    )

            YouTubeLivestream.objects.bulk_create(livestreams_to_create)
            YouTubeEndedLivestream.objects.bulk_create(
                ended_livestreams_to_create)

        return list(reversed(channel.livestreams.all()))

    def notified(self: 'YouTubeLivestream') -> None:
        self.is_new = False
        self.save()


# Ended livestreams model
class YouTubeEndedLivestream(YouTubeLivestreamParent):
    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE, related_name='ended_livestreams', related_query_name='ended_livestream')

    class Meta:
        verbose_name = 'Ended YouTube Livestream'
        verbose_name_plural = 'Ended YouTube Livestreams'

    @classmethod
    def is_ended_livestream(cls, channel: YouTubeChannel, video: Optional['YouTubeVideo'] = None, video_tuple: Optional[Tuple[str, str]] = None) -> bool:
        if video:
            return channel.ended_livestreams.filter(livestream_id=video.video_id, livestream_title=video.video_title).exists()
        else:
            return channel.ended_livestreams.filter(livestream_id=video_tuple[0], livestream_title=video_tuple[1]).exists()


# Parent of YouTubeVideo models
class YouTubeVideoParent(CreateUpdateTracker):
    video_id = models.CharField(max_length=20, **nb)
    video_title = models.CharField(max_length=256, **nb)
    is_saved_livestream = models.BooleanField(default=False, **nb)

    class Meta:
        abstract = True

    def __str__(self: 'YouTubeVideoParent'):
        return f'{self.video_title}'

    @property
    def video_url(self: 'YouTubeVideoParent') -> str:
        return f'https://www.youtube.com/watch?v={self.video_id}'


# YouTube video model
class YouTubeVideo(YouTubeVideoParent):
    is_new = models.BooleanField(default=False, **nb)
    is_reuploaded = models.BooleanField(default=False, **nb)
    iterations_skipped = models.PositiveSmallIntegerField(default=0, **nb)

    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE, related_name='videos', related_query_name='video')

    class Meta:
        verbose_name = 'YouTube Video'
        verbose_name_plural = 'YouTube Videos'

    @property
    def is_ended_livestream(self: 'YouTubeVideo') -> bool:
        return YouTubeEndedLivestream.is_ended_livestream(self.channel, self)

    @property
    def is_able_to_notify(self: 'YouTubeVideo') -> bool:
        return self.iterations_skipped > settings.ITERATIONS_TO_SKIP

    @classmethod
    def get_saved_video_data(cls, channel: Optional['YouTubeChannel'] = None) -> Dict[str, Tuple[str, bool, int]]:
        return {video.video_id: (video.video_title, video.is_saved_livestream, video.iterations_skipped) for video in (channel.videos.all() if channel else cls.objects.all())}

    @classmethod
    def get_new_videos(cls, channel: 'YouTubeChannel', videos: Dict[str, Tuple[str, bool]]) -> List['YouTubeVideo']:
        saved_videos = cls.get_saved_video_data(channel)

        if videos.keys() != saved_videos.keys() and len(videos) > 0:
            channel.clear_videos()
            is_new = True
            new_videos_count = 0
            videos_to_create = []
            deleted_videos_to_create = []

            for video_id in videos:
                is_been_deleted, is_counted_as_deleted_livestream = YouTubeDeletedVideo.is_been_deleted_and_counted_as_livestream(
                    channel, (video_id, videos[video_id][0]))
                is_reuploaded = YouTubeDeletedVideo.is_been_reuploaded(
                    channel, (video_id, videos[video_id][0]))

                is_new = False if not is_new else not (
                    video_id in saved_videos or is_been_deleted) or is_reuploaded

                new_videos_count = new_videos_count + \
                    (1 if not (video_id in saved_videos or is_been_deleted)
                     or is_reuploaded else 0)

                videos_to_create.append(
                    YouTubeVideo(
                        video_id=video_id,
                        video_title=videos[video_id][0],
                        is_saved_livestream=videos[video_id][1],
                        is_new=is_new,
                        iterations_skipped=saved_videos.get(
                            video_id, ('', '', 0))[2],
                        is_reuploaded=is_reuploaded,
                        channel=channel
                    )
                )

                if is_new and is_counted_as_deleted_livestream:
                    channel.decrement_deleted_livestreams()

            potentially_hidden_videos = list(saved_videos.keys())[
                slice(-new_videos_count, None)] if new_videos_count != 0 else []

            for saved_video_id in saved_videos:
                if not saved_video_id in videos and not saved_video_id in potentially_hidden_videos:
                    is_counted_as_deleted_livestream = saved_videos[saved_video_id][1] and YouTubeEndedLivestream.is_ended_livestream(
                        channel, video_tuple=(saved_video_id, saved_videos[saved_video_id][0]))

                    deleted_videos_to_create.append(
                        YouTubeDeletedVideo(
                            video_id=saved_video_id,
                            video_title=saved_videos[saved_video_id][0],
                            is_saved_livestream=saved_videos[saved_video_id][1],
                            is_counted_as_deleted_livestream=is_counted_as_deleted_livestream,
                            channel=channel
                        )
                    )

                    if is_counted_as_deleted_livestream:
                        channel.increment_deleted_livestreams()

            YouTubeVideo.objects.bulk_create(videos_to_create)
            YouTubeDeletedVideo.objects.bulk_create(deleted_videos_to_create)

        channel.set_not_new_if_all_videos_are_new()
        return list(reversed(channel.videos.all()))

    def notified(self: 'YouTubeVideo') -> None:
        self.is_new = False
        self.is_reuploaded = False
        self.iterations_skipped = 0
        self.save()

    def skip_iteration(self: 'YouTubeVideo') -> None:
        self.iterations_skipped = self.iterations_skipped + 1
        self.save()


# YouTube deleted video model
class YouTubeDeletedVideo(YouTubeVideoParent):
    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE, related_name='deleted_videos', related_query_name='deleted_video')

    is_counted_as_deleted_livestream = models.BooleanField(default=False, **nb)

    class Meta:
        verbose_name = 'Deleted YouTube Video'
        verbose_name_plural = 'Deleted YouTube Videos'

    @classmethod
    def is_been_deleted_and_counted_as_livestream(cls, channel: YouTubeChannel, video: Tuple[str, str]) -> bool:
        query_set = cls.objects.filter(Q(
            channel=channel, video_id__exact=video[0], video_title__exact=video[1]))
        reuploaded_video, is_deleted = query_set.first(), query_set.exists()
        is_counted_as_deleted_livestream = reuploaded_video.is_counted_as_deleted_livestream if reuploaded_video else False
        reuploaded_video.delete() if is_deleted else None
        return is_deleted, is_counted_as_deleted_livestream

    @classmethod
    def is_been_reuploaded(cls, channel: YouTubeChannel, video: Tuple[str, str]) -> bool:
        query_set = cls.objects.filter(~Q(video_id=video[0]) & Q(
            channel=channel, video_title__exact=video[1]))
        reuploaded_video, is_reuploaded = query_set.first(), query_set.exists()
        reuploaded_video.delete() if is_reuploaded else None
        return is_reuploaded


# Custom through model with title
class YouTubeChannelUserItem(ChannelUserItem):
    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE)

    @ property
    def type(self: 'YouTubeChannelUserItem') -> str:
        return 'youtube'


@receiver(models.signals.post_save, sender=YouTubeDeletedVideo)
@receiver(models.signals.post_save, sender=YouTubeEndedLivestream)
def remove_deleted_and_ended_content_after_time(sender, instance, *args, **kwargs):
    for deleted_video in YouTubeDeletedVideo.objects.all():
        if (now() - deleted_video.created_at).days >= 1:
            deleted_video.delete()

    for ended_livestream in YouTubeEndedLivestream.objects.all():
        if (now() - ended_livestream.created_at).days >= 1:
            ended_livestream.delete()


@receiver(models.signals.post_delete, sender=YouTubeChannelUserItem)
def clear_channels_content_if_no_subscribers(sender, instance, *args, **kwargs):
    for channel in YouTubeChannel.objects.filter(youtubechanneluseritem__isnull=True).distinct():
        channel.clear_content()


@receiver(models.signals.post_save, sender=YouTubeVideo)
def remove_deleted_video_if_it_in_videos(sender: 'YouTubeVideo', instance, *args, **kwargs):
    videos_ids = sender.get_saved_video_data().keys()
    queries = [Q(video_id__contains=video_id)
               for video_id in videos_ids]
    query = reduce(lambda x, y: x & y, queries)
    YouTubeDeletedVideo.objects.filter(query).delete()
