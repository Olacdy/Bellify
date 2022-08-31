import pytest
from bellify_bot.handlers.notification_handler import \
    get_notifications_urls_for_youtube_videos
from bellify_bot.models import User
from django.conf import settings
from tests.utils import (basic_user, create_youtube_channel_user_item,
                         premium_user, youtube_channel, youtube_new_video,
                         youtube_new_video_last_hidden,
                         youtube_new_video_reupload,
                         youtube_new_video_threshold_passed,
                         youtube_new_videos_beginning_and_middle,
                         youtube_one_livestream, youtube_videos)

from youtube.models import YouTubeLivestream, YouTubeVideo


@pytest.mark.django_db
def test_new_videos(basic_user, youtube_channel, youtube_videos, youtube_new_video):
    for video_id in youtube_videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=youtube_videos[video_id][0],
            published_at=youtube_videos[video_id][1],
            channel=youtube_channel
        )

    create_youtube_channel_user_item(basic_user, youtube_channel)
    videos_notification_urls_basic_users, _ = get_notifications_urls_for_youtube_videos(
        [youtube_channel], [youtube_new_video])

    assert list(youtube_new_video.keys(
    ))[0] in videos_notification_urls_basic_users[0]
    assert len(videos_notification_urls_basic_users) == 1


@pytest.mark.django_db
def test_new_video_reupload(basic_user, youtube_channel, youtube_videos, youtube_new_video_reupload):
    for video_id in youtube_videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=youtube_videos[video_id][0],
            published_at=youtube_videos[video_id][1],
            channel=youtube_channel
        )

    create_youtube_channel_user_item(basic_user, youtube_channel)
    videos_notification_urls_basic_users, _ = get_notifications_urls_for_youtube_videos(
        [youtube_channel], [youtube_new_video_reupload])

    assert list(youtube_new_video_reupload.keys(
    ))[0] in videos_notification_urls_basic_users[0]
    assert len(videos_notification_urls_basic_users) == 1


@pytest.mark.django_db
def test_new_video_threshold_passed(basic_user, youtube_channel, youtube_videos, youtube_new_video_threshold_passed):
    for video_id in youtube_videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=youtube_videos[video_id][0],
            published_at=youtube_videos[video_id][1],
            channel=youtube_channel
        )

    create_youtube_channel_user_item(basic_user, youtube_channel)
    videos_notification_urls_basic_users, _ = get_notifications_urls_for_youtube_videos(
        [youtube_channel], [youtube_new_video_threshold_passed])

    assert list(youtube_new_video_threshold_passed.keys(
    ))[0] == youtube_channel.videos.last().video_id
    assert len(videos_notification_urls_basic_users) == 0


@pytest.mark.django_db
def test_new_video_last_hidden(basic_user, youtube_channel, youtube_videos, youtube_new_video_last_hidden):
    for video_id in youtube_videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=youtube_videos[video_id][0],
            published_at=youtube_videos[video_id][1],
            channel=youtube_channel
        )

    create_youtube_channel_user_item(basic_user, youtube_channel)
    videos_notification_urls_basic_users, _ = get_notifications_urls_for_youtube_videos(
        [youtube_channel], [youtube_new_video_last_hidden])

    assert list(youtube_new_video_last_hidden.keys(
    ))[0] in videos_notification_urls_basic_users[0]
    assert len(videos_notification_urls_basic_users) == 1


@pytest.mark.django_db
def test_new_video_gets_hidden(basic_user, youtube_channel, youtube_videos, youtube_new_video):
    for video_id in youtube_videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=youtube_videos[video_id][0],
            published_at=youtube_videos[video_id][1],
            channel=youtube_channel
        )

    create_youtube_channel_user_item(basic_user, youtube_channel)
    videos_notification_urls_basic_users_one_new, _ = get_notifications_urls_for_youtube_videos(
        [youtube_channel], [youtube_new_video])
    videos_notification_urls_basic_users_last_hidden, _ = get_notifications_urls_for_youtube_videos(
        [youtube_channel], [youtube_videos])

    assert len(videos_notification_urls_basic_users_one_new) == 1
    assert len(videos_notification_urls_basic_users_last_hidden) == 0


@pytest.mark.django_db
def test_new_videos_beginning_and_middle(basic_user, youtube_channel, youtube_videos, youtube_new_videos_beginning_and_middle):
    for video_id in youtube_videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=youtube_videos[video_id][0],
            published_at=youtube_videos[video_id][1],
            channel=youtube_channel
        )

    create_youtube_channel_user_item(basic_user, youtube_channel)
    videos_notification_urls_basic_users, _ = get_notifications_urls_for_youtube_videos(
        [youtube_channel], [youtube_new_videos_beginning_and_middle])

    assert list(youtube_new_videos_beginning_and_middle.keys(
    ))[0] in videos_notification_urls_basic_users[0]
    assert len(videos_notification_urls_basic_users) == 2


@pytest.mark.django_db
def test_content_clear(youtube_channel, youtube_videos, youtube_one_livestream):
    for video_id in youtube_videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=youtube_videos[video_id][0],
            published_at=youtube_videos[video_id][1],
            channel=youtube_channel
        )

    for livestream_id in youtube_one_livestream:
        YouTubeLivestream.objects.create(
            livestream_id=livestream_id,
            livestream_title=youtube_one_livestream[livestream_id],
            channel=youtube_channel
        )

    basic_user_1 = User.objects.create(
        user_id='325066505',
        username='golovakanta1',
        status='B'
    )

    basic_user_2 = User.objects.create(
        user_id='325066506',
        username='golovakanta2',
        status='B'
    )

    premium_user = User.objects.create(
        user_id='325066507',
        username='golovakanta3',
        status='P'
    )

    basic_user_1_channel_user_item = create_youtube_channel_user_item(
        basic_user_1, youtube_channel)
    _ = create_youtube_channel_user_item(
        basic_user_2, youtube_channel)
    premium_user_channel_user_item = create_youtube_channel_user_item(
        premium_user, youtube_channel)

    assert len(youtube_channel.livestreams.all()) > 0

    basic_user_1_channel_user_item.delete()

    assert len(youtube_channel.livestreams.all()) > 0

    premium_user_channel_user_item.delete()

    assert len(youtube_channel.livestreams.all()) == 0
