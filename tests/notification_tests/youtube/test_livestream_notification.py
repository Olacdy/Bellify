import pytest
from bellify_bot.handlers.notification_handler import (
    get_notifications_urls_for_youtube_livestreams,
    get_notifications_urls_for_youtube_videos)
from django.conf import settings
from youtube.models import YouTubeLivestream, YouTubeVideo

from tests.utils import (basic_user, youtube_channel, youtube_channel_deleted_livestreams_0,
                         youtube_channel_deleted_livestreams_1,
                         create_youtube_channel_user_item, youtube_livestreams, youtube_one_livestream,
                         youtube_one_saved_livestream, premium_user, youtube_videos)


@pytest.mark.django_db
def test_livestream_notification_for_basic_user(basic_user, youtube_channel, youtube_one_livestream):
    create_youtube_channel_user_item(basic_user, youtube_channel)
    livestreams_notification_urls = get_notifications_urls_for_youtube_livestreams(
        [youtube_channel], [youtube_one_livestream])

    assert len(livestreams_notification_urls) == 0


@pytest.mark.django_db
def test_livestream_notification_for_premium_user(premium_user, youtube_channel, youtube_one_livestream):
    create_youtube_channel_user_item(premium_user, youtube_channel)
    livestreams_notification_urls = get_notifications_urls_for_youtube_livestreams(
        [youtube_channel], [youtube_one_livestream])

    assert len(livestreams_notification_urls) == 1


@pytest.mark.django_db
def test_saved_livestream_notification_for_basic_user(basic_user, youtube_channel, youtube_videos, youtube_livestreams, youtube_one_livestream, youtube_one_saved_livestream):
    for video_id in youtube_videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=youtube_videos[video_id][0],
            published_at=youtube_videos[video_id][1],
            channel=youtube_channel
        )

    for livestream_id in youtube_livestreams:
        YouTubeLivestream.objects.create(
            livestream_id=livestream_id,
            livestream_title=youtube_livestreams[livestream_id],
            channel=youtube_channel
        )

    create_youtube_channel_user_item(basic_user, youtube_channel)
    _, videos_notification_urls_basic_users_first_iteration, _ = get_notifications_urls_for_youtube_livestreams(
        [youtube_channel], [youtube_one_livestream]), *get_notifications_urls_for_youtube_videos([youtube_channel], [youtube_one_saved_livestream])
    _, videos_notification_urls_basic_users_second_iteration, _ = get_notifications_urls_for_youtube_livestreams(
        [youtube_channel], [youtube_one_livestream]), *get_notifications_urls_for_youtube_videos([youtube_channel], [youtube_one_saved_livestream])

    assert list(youtube_one_livestream.keys())[
        0] in videos_notification_urls_basic_users_first_iteration[0]
    assert len(videos_notification_urls_basic_users_first_iteration) == 1
    assert len(videos_notification_urls_basic_users_second_iteration) == 0


@pytest.mark.django_db
def test_first_saved_livestream_notification_for_premium_user(premium_user, youtube_channel, youtube_videos, youtube_livestreams, youtube_one_livestream, youtube_one_saved_livestream):
    for video_id in youtube_videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=youtube_videos[video_id][0],
            published_at=youtube_videos[video_id][1],
            channel=youtube_channel
        )

    for livestream_id in youtube_livestreams:
        YouTubeLivestream.objects.create(
            livestream_id=livestream_id,
            livestream_title=youtube_livestreams[livestream_id],
            channel=youtube_channel
        )

    create_youtube_channel_user_item(premium_user, youtube_channel)
    _, _, videos_notification_urls_premium_users_first_iteration = get_notifications_urls_for_youtube_livestreams(
        [youtube_channel], [youtube_one_livestream]), *get_notifications_urls_for_youtube_videos([youtube_channel], [youtube_one_saved_livestream])
    for _ in range(settings.ITERATIONS_TO_SKIP):
        _, _, videos_notification_urls_premium_users_final_iteration = get_notifications_urls_for_youtube_livestreams(
            [youtube_channel], [youtube_one_livestream]), *get_notifications_urls_for_youtube_videos([youtube_channel], [youtube_one_saved_livestream])

    assert len(videos_notification_urls_premium_users_first_iteration) == 0
    assert len(videos_notification_urls_premium_users_final_iteration) == 1
    assert youtube_channel.deleted_livestreams == 0


@pytest.mark.django_db
def test_second_saved_livestream_if_channel_does_not_delete_its_livestreams_notification_for_premium_user(premium_user, youtube_channel_deleted_livestreams_0, youtube_videos, youtube_livestreams, youtube_one_livestream, youtube_one_saved_livestream):
    for video_id in youtube_videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=youtube_videos[video_id][0],
            published_at=youtube_videos[video_id][1],
            channel=youtube_channel_deleted_livestreams_0
        )

    for livestream_id in youtube_livestreams:
        YouTubeLivestream.objects.create(
            livestream_id=livestream_id,
            livestream_title=youtube_livestreams[livestream_id],
            channel=youtube_channel_deleted_livestreams_0
        )

    create_youtube_channel_user_item(
        premium_user, youtube_channel_deleted_livestreams_0)
    _, _, videos_notification_urls_premium_users_first_iteration = get_notifications_urls_for_youtube_livestreams(
        [youtube_channel_deleted_livestreams_0], [youtube_one_livestream]), *get_notifications_urls_for_youtube_videos([youtube_channel_deleted_livestreams_0], [youtube_one_saved_livestream])

    assert len(videos_notification_urls_premium_users_first_iteration) == 1
    assert youtube_channel_deleted_livestreams_0.deleted_livestreams == 0


@pytest.mark.django_db
def test_second_saved_livestream_if_channel_does_delete_its_livestreams_notification_for_premium_user(premium_user, youtube_channel_deleted_livestreams_1, youtube_videos, youtube_livestreams, youtube_one_livestream, youtube_one_saved_livestream):
    for video_id in youtube_videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=youtube_videos[video_id][0],
            published_at=youtube_videos[video_id][1],
            channel=youtube_channel_deleted_livestreams_1
        )

    for livestream_id in youtube_livestreams:
        YouTubeLivestream.objects.create(
            livestream_id=livestream_id,
            livestream_title=youtube_livestreams[livestream_id],
            channel=youtube_channel_deleted_livestreams_1
        )

    create_youtube_channel_user_item(
        premium_user, youtube_channel_deleted_livestreams_1)
    _, _, videos_notification_urls_premium_users_first_iteration = get_notifications_urls_for_youtube_livestreams(
        [youtube_channel_deleted_livestreams_1], [youtube_one_livestream]), *get_notifications_urls_for_youtube_videos([youtube_channel_deleted_livestreams_1], [youtube_one_saved_livestream])
    for _ in range(settings.ITERATIONS_TO_SKIP):
        _, _, videos_notification_urls_premium_users_final_iteration = get_notifications_urls_for_youtube_livestreams(
            [youtube_channel_deleted_livestreams_1], [youtube_one_livestream]), *get_notifications_urls_for_youtube_videos([youtube_channel_deleted_livestreams_1], [youtube_one_saved_livestream])

    assert len(videos_notification_urls_premium_users_first_iteration) == 0
    assert len(videos_notification_urls_premium_users_final_iteration) == 1
    assert youtube_channel_deleted_livestreams_1.deleted_livestreams == 0
