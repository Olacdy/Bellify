import pytest
from bellify_bot.handlers.notification_handler import (
    get_notifications_urls_for_youtube_livestreams,
    get_notifications_urls_for_youtube_videos)
from django.conf import settings
from youtube.models import YouTubeLivestream, YouTubeVideo

from tests.utils import (basic_user, channel, channel_deleted_livestreams_0,
                         channel_deleted_livestreams_1,
                         create_channel_user_item, livestreams, one_livestream,
                         one_saved_livestream, premium_user, videos)


@pytest.mark.django_db
def test_livestream_notification_for_basic_user(basic_user, channel, one_livestream):
    create_channel_user_item(basic_user, channel)
    livestreams_notification_urls = get_notifications_urls_for_youtube_livestreams(
        [channel], [one_livestream])

    assert len(livestreams_notification_urls) == 0


@pytest.mark.django_db
def test_livestream_notification_for_premium_user(premium_user, channel, one_livestream):
    create_channel_user_item(premium_user, channel)
    livestreams_notification_urls = get_notifications_urls_for_youtube_livestreams(
        [channel], [one_livestream])

    assert len(livestreams_notification_urls) == 1


@pytest.mark.django_db
def test_saved_livestream_notification_for_basic_user(basic_user, channel, videos, livestreams, one_livestream, one_saved_livestream):
    for video_id in videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=videos[video_id][0],
            published_datetime=videos[video_id][1],
            channel=channel
        )

    for livestream_id in livestreams:
        YouTubeLivestream.objects.create(
            livestream_id=livestream_id,
            livestream_title=livestreams[livestream_id],
            channel=channel
        )

    create_channel_user_item(basic_user, channel)
    _, videos_notification_urls_basic_users_first_iteration, _ = get_notifications_urls_for_youtube_livestreams(
        [channel], [one_livestream]), *get_notifications_urls_for_youtube_videos([channel], [one_saved_livestream])
    _, videos_notification_urls_basic_users_second_iteration, _ = get_notifications_urls_for_youtube_livestreams(
        [channel], [one_livestream]), *get_notifications_urls_for_youtube_videos([channel], [one_saved_livestream])

    assert 'test_id_1' in videos_notification_urls_basic_users_first_iteration[0]
    assert len(videos_notification_urls_basic_users_first_iteration) == 1
    assert len(videos_notification_urls_basic_users_second_iteration) == 0


@pytest.mark.django_db
def test_first_saved_livestream_notification_for_premium_user(premium_user, channel, videos, livestreams, one_livestream, one_saved_livestream):
    for video_id in videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=videos[video_id][0],
            published_datetime=videos[video_id][1],
            channel=channel
        )

    for livestream_id in livestreams:
        YouTubeLivestream.objects.create(
            livestream_id=livestream_id,
            livestream_title=livestreams[livestream_id],
            channel=channel
        )

    create_channel_user_item(premium_user, channel)
    _, _, videos_notification_urls_premium_users_first_iteration = get_notifications_urls_for_youtube_livestreams(
        [channel], [one_livestream]), *get_notifications_urls_for_youtube_videos([channel], [one_saved_livestream])
    for _ in range(settings.ITERATIONS_TO_SKIP):
        _, _, videos_notification_urls_premium_users_final_iteration = get_notifications_urls_for_youtube_livestreams(
            [channel], [one_livestream]), *get_notifications_urls_for_youtube_videos([channel], [one_saved_livestream])

    assert len(videos_notification_urls_premium_users_first_iteration) == 0
    assert len(videos_notification_urls_premium_users_final_iteration) == 1
    assert channel.deleted_livestreams == 0


@pytest.mark.django_db
def test_second_saved_livestream_if_channel_does_not_delete_its_livestreams_notification_for_premium_user(premium_user, channel_deleted_livestreams_0, videos, livestreams, one_livestream, one_saved_livestream):
    for video_id in videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=videos[video_id][0],
            published_datetime=videos[video_id][1],
            channel=channel_deleted_livestreams_0
        )

    for livestream_id in livestreams:
        YouTubeLivestream.objects.create(
            livestream_id=livestream_id,
            livestream_title=livestreams[livestream_id],
            channel=channel_deleted_livestreams_0
        )

    create_channel_user_item(premium_user, channel_deleted_livestreams_0)
    _, _, videos_notification_urls_premium_users_first_iteration = get_notifications_urls_for_youtube_livestreams(
        [channel_deleted_livestreams_0], [one_livestream]), *get_notifications_urls_for_youtube_videos([channel_deleted_livestreams_0], [one_saved_livestream])

    assert len(videos_notification_urls_premium_users_first_iteration) == 1
    assert channel_deleted_livestreams_0.deleted_livestreams == 0


@pytest.mark.django_db
def test_second_saved_livestream_if_channel_does_delete_its_livestreams_notification_for_premium_user(premium_user, channel_deleted_livestreams_1, videos, livestreams, one_livestream, one_saved_livestream):
    for video_id in videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=videos[video_id][0],
            published_datetime=videos[video_id][1],
            channel=channel_deleted_livestreams_1
        )

    for livestream_id in livestreams:
        YouTubeLivestream.objects.create(
            livestream_id=livestream_id,
            livestream_title=livestreams[livestream_id],
            channel=channel_deleted_livestreams_1
        )

    create_channel_user_item(premium_user, channel_deleted_livestreams_1)
    _, _, videos_notification_urls_premium_users_first_iteration = get_notifications_urls_for_youtube_livestreams(
        [channel_deleted_livestreams_1], [one_livestream]), *get_notifications_urls_for_youtube_videos([channel_deleted_livestreams_1], [one_saved_livestream])
    for _ in range(settings.ITERATIONS_TO_SKIP):
        _, _, videos_notification_urls_premium_users_final_iteration = get_notifications_urls_for_youtube_livestreams(
            [channel_deleted_livestreams_1], [one_livestream]), *get_notifications_urls_for_youtube_videos([channel_deleted_livestreams_1], [one_saved_livestream])

    assert len(videos_notification_urls_premium_users_first_iteration) == 0
    assert len(videos_notification_urls_premium_users_final_iteration) == 1
    assert channel_deleted_livestreams_1.deleted_livestreams == 0
