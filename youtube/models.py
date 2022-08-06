from functools import reduce
from typing import List, Optional, Tuple, Union

from bellify_bot.models import Channel, ChannelUserItem, User
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.utils.timezone import now

from utils.models import CreateUpdateTracker, nb


# YouTube channel model
class YouTubeChannel(Channel):
    users = models.ManyToManyField(
        User, through='YouTubeChannelUserItem')
    deleted_livestreams = models.PositiveIntegerField(default=0, **nb)

    class Meta:
        verbose_name = 'YouTube Channel'
        verbose_name_plural = 'YouTube Channels'

    def __str__(self):
        return f'{self.channel_title}'

    @property
    def type(self: 'YouTubeChannel') -> str:
        return 'youtube'

    @property
    def last_video(self: 'YouTubeChannel') -> Union['YouTubeVideo', bool]:
        video = self.videos.all().first()
        return video if video else False

    @property
    def ongoing_livestream(self: 'YouTubeChannel') -> Union['YouTubeLivestream', bool]:
        livestream = self.livestreams.all().first()
        return livestream if livestream else False

    @property
    def is_livestreaming(self: 'YouTubeChannel') -> bool:
        return bool(self.ongoing_livestream)

    @property
    def is_deleting_livestreams(self: 'YouTubeChannel') -> bool:
        return bool(self.deleted_livestreams)

    def increment_deleted_livestreams(self: 'YouTubeChannel') -> None:
        self.deleted_livestreams = self.deleted_livestreams + 1
        self.save()


# Parent of YouTubeLivestream models
class YouTubeLivestreamParent(CreateUpdateTracker):
    livestream_id = models.CharField(max_length=20, **nb)
    livestream_title = models.CharField(max_length=256, **nb)

    class Meta:
        abstract = True

    def __str__(self: 'YouTubeLivestreamParent'):
        return f'{self.livestream_title}'

    @property
    def livestream_url(self: 'YouTubeLivestreamParent'):
        return f'https://www.youtube.com/watch?v={self.livestream_id}'

    @property
    def tuple(self: 'YouTubeLivestreamParent'):
        return self.livestream_id, self.livestream_title


# YouTube livestream model
class YouTubeLivestream(YouTubeLivestreamParent):
    is_notified = models.BooleanField(default=True, **nb)

    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE, related_name='livestreams', related_query_name='livestream')

    class Meta:
        verbose_name = 'YouTube Livestream'
        verbose_name_plural = 'YouTube Livestreams'

    @classmethod
    def get_tuples_and_ids(cls, channel: Optional['YouTubeChannel'] = None):
        if channel:
            saved_livestreams_tuples = [
                livestreams.tuple for livestreams in channel.livestreams.all()]
            return saved_livestreams_tuples, [saved_livestreams_tuple[0]
                                              for saved_livestreams_tuple in saved_livestreams_tuples]
        else:
            saved_livestreams_tuples = [
                livestreams.tuple for livestreams in cls.objects.all()]
            return saved_livestreams_tuples, [saved_livestreams_tuple[0]
                                              for saved_livestreams_tuple in saved_livestreams_tuples]

    @classmethod
    def get_new_livestreams(cls, channel: YouTubeChannel, livestreams: 'YouTubeLivestream') -> List['YouTubeLivestream']:
        saved_livestreams_tuples, saved_livestreams_ids = cls.get_tuples_and_ids(
            channel)
        livestreams_ids = [livestream[0] for livestream in livestreams]

        if livestreams != saved_livestreams_tuples:
            for livestream in livestreams:
                if not livestream in saved_livestreams_tuples:
                    YouTubeLivestream.objects.get_or_create(
                        livestream_id=livestream[0],
                        livestream_title=livestream[1],
                        is_notified=False,
                        channel=channel
                    )

        if livestreams != saved_livestreams_tuples:
            channel.livestreams.all().delete()
            disable_notifications = False

            for livestream in livestreams:
                disable_notifications = livestream[0] in saved_livestreams_ids or disable_notifications
                YouTubeLivestream.objects.get_or_create(
                    livestream_id=livestream[0],
                    livestream_title=livestream[1],
                    is_notified=disable_notifications,
                    channel=channel
                )

            for saved_livestream_tuple in saved_livestreams_tuples:
                if not saved_livestream_tuple[0] in livestreams_ids:
                    YouTubeEndedLivestream.objects.get_or_create(
                        livestream_id=saved_livestream_tuple[0],
                        livestream_title=saved_livestream_tuple[1],
                        channel=channel
                    )

        return reversed(channel.livestreams.all())

    def notified(self: 'YouTubeLivestream') -> None:
        self.is_notified = True
        self.save()


# Ended livestreams model
class YouTubeEndedLivestream(YouTubeLivestreamParent):
    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE, related_name='ended_livestreams', related_query_name='ended_livestream')

    class Meta:
        verbose_name = 'Ended YouTube Livestream'
        verbose_name_plural = 'Ended YouTube Livestreams'

    @classmethod
    def is_in_ended_stream(cls, channel: YouTubeChannel, video: 'YouTubeVideo') -> bool:
        return channel.ended_livestreams.filter(livestream_id=video.video_id, livestream_title=video.video_title).exists()


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
    def video_url(self: 'YouTubeVideoParent'):
        return f'https://www.youtube.com/watch?v={self.video_id}'

    @property
    def tuple(self: 'YouTubeVideoParent') -> Tuple[str, str, bool]:
        return self.video_id, self.video_title, self.is_saved_livestream


# YouTube video model
class YouTubeVideo(YouTubeVideoParent):
    is_notified = models.BooleanField(default=True, **nb)
    is_reuploaded = models.BooleanField(default=False, **nb)
    iterations_skipped = models.PositiveSmallIntegerField(default=0, **nb)

    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE, related_name='videos', related_query_name='video')

    class Meta:
        verbose_name = 'YouTube Video'
        verbose_name_plural = 'YouTube Videos'

    @property
    def is_able_to_notify(self: 'YouTubeVideo') -> bool:
        return self.iterations_skipped > settings.ITERATIONS_TO_SKIP

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
        saved_videos_tuples, saved_videos_ids = cls.get_tuples_and_ids(channel)
        videos_ids = [video[0] for video in videos]

        if videos != saved_videos_tuples:
            channel.videos.all().delete()
            disable_notifications = False

            for video in videos:
                disable_notifications = video[0] in saved_videos_ids or disable_notifications
                is_reuploaded = YouTubeDeletedVideo.is_video_was_deleted(
                    channel, video[1])
                YouTubeVideo.objects.get_or_create(
                    video_id=video[0],
                    video_title=video[1],
                    is_saved_livestream=video[2],
                    is_notified=disable_notifications,
                    is_reuploaded=is_reuploaded,
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
                    channel.increment_deleted_livestreams()

        return reversed(channel.videos.all())

    def notified(self: 'YouTubeVideo') -> None:
        self.is_notified = True
        self.is_reuploaded = False
        self.save()

    def skip_iteration(self: 'YouTubeVideo') -> None:
        self.iterations_skipped = self.iterations_skipped + 1
        self.save()


# YouTube deleted video model
class YouTubeDeletedVideo(YouTubeVideoParent):
    channel = models.ForeignKey(
        YouTubeChannel, on_delete=models.CASCADE, related_name='deleted_videos', related_query_name='deleted_video')

    class Meta:
        verbose_name = 'Deleted YouTube Video'
        verbose_name_plural = 'Deleted YouTube Videos'

    @classmethod
    def is_video_was_deleted(cls, channel: YouTubeChannel, video: YouTubeVideo) -> bool:
        query_set = cls.objects.filter(
            channel=channel, video_title__contains=video[1])
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
        if (now() - deleted_video.created_at).days > 1:
            deleted_video.delete()

    for ended_livestream in YouTubeEndedLivestream.objects.all():
        if (now() - ended_livestream.created_at).days > 1:
            ended_livestream.delete()


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
