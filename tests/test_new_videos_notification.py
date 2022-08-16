import pytest
from bellify_bot.handlers.notification_handler import \
    get_notifications_urls_for_youtube_videos
from django.conf import settings
from youtube.models import YouTubeDeletedVideo, YouTubeVideo

from tests.utils import (basic_user, channel, create_channel_user_item,
                         one_new_video,
                         one_new_video_in_the_beginning_and_one_in_the_middle,
                         one_new_video_last_one_hidden, premium_user, videos)


@pytest.mark.django_db
def test_set_new_videos(basic_user, channel, videos, one_new_video):
    for video_id in videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=videos[video_id][0],
            is_saved_livestream=videos[video_id][1],
            channel=channel
        )

    create_channel_user_item(basic_user, channel)
    videos_notification_urls_basic_users, _ = get_notifications_urls_for_youtube_videos(
        [channel], [one_new_video])

    assert f'https://api.telegram.org/bot{settings.TOKEN}/sendMessage?chat_id={basic_user.user_id}' in videos_notification_urls_basic_users[
        0]

    assert 'MHUnaXJqWF4' in videos_notification_urls_basic_users[0]

    assert len(videos_notification_urls_basic_users) == 1


@pytest.mark.django_db
def test_new_video_last_one_hidden(basic_user, channel, videos, one_new_video_last_one_hidden):
    for video_id in videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=videos[video_id][0],
            is_saved_livestream=videos[video_id][1],
            channel=channel
        )

    create_channel_user_item(basic_user, channel)
    videos_notification_urls_basic_users, _ = get_notifications_urls_for_youtube_videos(
        [channel], [one_new_video_last_one_hidden])

    assert f'https://api.telegram.org/bot{settings.TOKEN}/sendMessage?chat_id={basic_user.user_id}' in videos_notification_urls_basic_users[
        0]
    assert 'MHUnaXJqWF4' in videos_notification_urls_basic_users[0]
    assert len(videos_notification_urls_basic_users) == 1
    assert len(YouTubeDeletedVideo.objects.all()) == 0


@pytest.mark.django_db
def test_new_video_gets_hidden(basic_user, channel, videos, one_new_video):
    for video_id in videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=videos[video_id][0],
            is_saved_livestream=videos[video_id][1],
            channel=channel
        )

    create_channel_user_item(basic_user, channel)
    YouTubeVideo.get_new_videos(channel, one_new_video)
    videos_notification_urls_basic_users, _ = get_notifications_urls_for_youtube_videos(
        [channel], [videos])

    assert len(videos_notification_urls_basic_users) == 0
    assert YouTubeDeletedVideo.objects.all()[
        0].video_id == list(one_new_video.keys())[0]


@pytest.mark.django_db
def test_new_videos_in_the_beginning_and_in_the_middle(basic_user, channel, videos, one_new_video_in_the_beginning_and_one_in_the_middle):
    for video_id in videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=videos[video_id][0],
            is_saved_livestream=videos[video_id][1],
            channel=channel
        )

    create_channel_user_item(basic_user, channel)
    videos_notification_urls_basic_users, _ = get_notifications_urls_for_youtube_videos(
        [channel], [one_new_video_in_the_beginning_and_one_in_the_middle])

    assert 'test_id_1' in videos_notification_urls_basic_users[0]
    assert len(videos_notification_urls_basic_users) == 1
