import itertools

import pytest
from bellify_bot.handlers.bot_handlers.utils import get_urls_to_notify
from bellify_bot.models import User
from django.conf import settings
from youtube.models import YouTubeChannel, YouTubeLivestream, YouTubeEndedLivestream, YouTubeChannelUserItem, YouTubeDeletedVideo, YouTubeVideo


def check_youtube(channel, new_videos, new_livestreams) -> None:
    livestream_notification_urls = []
    video_notification_urls = []

    for livestream in new_livestreams:
        if livestream.is_new:
            livestream_notification_urls.append(get_urls_to_notify(users=[item.user for item in YouTubeChannelUserItem.objects.filter(
                channel=channel, user__status='P')], channel_id=channel.channel_id, url=livestream.livestream_url,
                content_title=livestream.livestream_title, is_live=True))
            livestream.notified()

    for video in new_videos:
        if video.is_new and not video.iterations_skipped > 0:
            video_notification_urls.append(get_urls_to_notify(users=[item.user for item in YouTubeChannelUserItem.objects.filter(
                channel=channel, user__status='B')], channel_id=channel.channel_id, url=video.video_url,
                content_title=video.video_title, is_reuploaded=video.is_reuploaded))

        if video.is_new or video.iterations_skipped > 0:
            if video.is_ended_livestream and channel.check_for_deleting_livestreams and not video.is_able_to_notify:
                video.skip_iteration()
            else:
                video_notification_urls.append(get_urls_to_notify(users=[item.user for item in YouTubeChannelUserItem.objects.filter(
                    channel=channel, user__status='P')], channel_id=channel.channel_id, url=video.video_url,
                    content_title=video.video_title, is_reuploaded=video.is_reuploaded,
                    is_ended_livestream=video.is_ended_livestream, is_might_be_deleted=channel.is_deleting_livestreams))
                video.notified()

    return list(itertools.chain.from_iterable(
        video_notification_urls + livestream_notification_urls))


@pytest.fixture()
def basic_user():
    return User.objects.create(
        user_id='325066507',
        username='golovakanta',
    )


@pytest.fixture()
def premium_user():
    return User.objects.create(
        user_id='325066507',
        username='golovakanta',
        status='P'
    )


@pytest.fixture()
def channel():
    return YouTubeChannel.objects.create(
        channel_id='UCcAd5Np7fO8SeejB1FVKcYw',
        channel_title='Best Ever Food Review Show',
    )


@pytest.fixture()
def channel_deleted_livestreams_0():
    return YouTubeChannel.objects.create(
        channel_id='UCcAd5Np7fO8SeejB1FVKcYw',
        channel_title='Best Ever Food Review Show',
        deleted_livestreams=0,
    )


@pytest.fixture()
def channel_deleted_livestreams_1():
    return YouTubeChannel.objects.create(
        channel_id='UCcAd5Np7fO8SeejB1FVKcYw',
        channel_title='Best Ever Food Review Show',
        deleted_livestreams=1,
    )


@pytest.fixture()
def videos():
    return {
        'bol-_4NZjWE': ('Buffalo Placenta!! World’s Most Bizarre Vegan Food!!', False),
        'INJK-vTKPdg': ('The Surprising Noodle Vietnam Loves Most!! It’s Not Pho!!', False),
        '1H2l7dHq1fs': ('Blood Red Jellyfish!! EXTREME Vietnam Street Food!!', False),
        'FSogD7bAHF8': ('$1 VS $152 Filipino Lechon!! Manila’s Meat Masterpiece!!', False),
        'v0NNI5wS_GM': ('Filipino Street Food That Will Kill You!! Manila Heart Attack Tour!!', False),
        'VXjrCIcGZmw': ('Bizarre Filipino Food in Pampanga!! Pets, Pigs and Pests!!', False),
    }


@pytest.fixture()
def livestreams():
    return {
        'test_id_1': 'Test Livestream 1',
        'test_id_2': 'Test Livestream 2',
    }


@pytest.fixture()
def one_livestream():
    return {
        'test_id_2': 'Test Livestream 2',
    }


@pytest.fixture()
def one_saved_livestream():
    return {
        'test_id_1': ('Test Livestream 1', True),
        'bol-_4NZjWE': ('Buffalo Placenta!! World’s Most Bizarre Vegan Food!!', False),
        'INJK-vTKPdg': ('The Surprising Noodle Vietnam Loves Most!! It’s Not Pho!!', False),
        '1H2l7dHq1fs': ('Blood Red Jellyfish!! EXTREME Vietnam Street Food!!', False),
        'FSogD7bAHF8': ('$1 VS $152 Filipino Lechon!! Manila’s Meat Masterpiece!!', False),
        'v0NNI5wS_GM': ('Filipino Street Food That Will Kill You!! Manila Heart Attack Tour!!', False),
    }


def create_channel_user_item(user, channel):
    return YouTubeChannelUserItem.objects.create(
        user=user,
        channel=channel
    )


@pytest.mark.django_db
def test_livestream_notification_for_basic_user(basic_user, channel, one_livestream):
    create_channel_user_item(basic_user, channel)
    urls_to_notify = check_youtube(
        channel, YouTubeVideo.get_new_videos(channel, {}), YouTubeLivestream.get_new_livestreams(channel, one_livestream))

    assert len(urls_to_notify) == 0


@pytest.mark.django_db
def test_livestream_notification_for_premium_user(premium_user, channel, one_livestream):
    create_channel_user_item(premium_user, channel)
    urls_to_notify = check_youtube(
        channel, YouTubeVideo.get_new_videos(channel, {}), YouTubeLivestream.get_new_livestreams(channel, one_livestream))

    assert len(urls_to_notify) == 1


@pytest.mark.django_db
def test_saved_livestream_notification_for_basic_user(basic_user, channel, videos, livestreams, one_livestream, one_saved_livestream):
    for video_id in videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=videos[video_id][0],
            is_saved_livestream=videos[video_id][1],
            channel=channel
        )

    for livestream_id in livestreams:
        YouTubeLivestream.objects.create(
            livestream_id=livestream_id,
            livestream_title=livestreams[livestream_id],
            channel=channel
        )

    create_channel_user_item(basic_user, channel)
    urls_to_notify_first_iteration = check_youtube(
        channel, YouTubeVideo.get_new_videos(channel, one_saved_livestream), YouTubeLivestream.get_new_livestreams(channel, one_livestream))
    urls_to_notify_second_iteration = check_youtube(
        channel, YouTubeVideo.get_new_videos(channel, one_saved_livestream), YouTubeLivestream.get_new_livestreams(channel, one_livestream))

    assert 'test_id_1' in urls_to_notify_first_iteration[0]
    assert len(urls_to_notify_first_iteration) == 1
    assert len(urls_to_notify_second_iteration) == 0


@pytest.mark.django_db
def test_first_saved_livestream_notification_for_premium_user(premium_user, channel, videos, livestreams, one_livestream, one_saved_livestream):
    for video_id in videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=videos[video_id][0],
            is_saved_livestream=videos[video_id][1],
            channel=channel
        )

    for livestream_id in livestreams:
        YouTubeLivestream.objects.create(
            livestream_id=livestream_id,
            livestream_title=livestreams[livestream_id],
            channel=channel
        )

    create_channel_user_item(premium_user, channel)
    urls_to_notify_first_iteration = check_youtube(
        channel, YouTubeVideo.get_new_videos(channel, one_saved_livestream), YouTubeLivestream.get_new_livestreams(channel, one_livestream))
    for _ in range(settings.ITERATIONS_TO_SKIP + 1):
        urls_to_notify_final_iteration = check_youtube(
            channel, YouTubeVideo.get_new_videos(channel, one_saved_livestream), YouTubeLivestream.get_new_livestreams(channel, one_livestream))

    assert len(urls_to_notify_first_iteration) == 0
    assert len(urls_to_notify_final_iteration) == 1
    assert channel.deleted_livestreams == 0


@pytest.mark.django_db
def test_second_saved_livestream_if_channel_does_not_delete_its_livestreams_notification_for_premium_user(premium_user, channel_deleted_livestreams_0, videos, livestreams, one_livestream, one_saved_livestream):
    for video_id in videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=videos[video_id][0],
            is_saved_livestream=videos[video_id][1],
            channel=channel_deleted_livestreams_0
        )

    for livestream_id in livestreams:
        YouTubeLivestream.objects.create(
            livestream_id=livestream_id,
            livestream_title=livestreams[livestream_id],
            channel=channel_deleted_livestreams_0
        )

    create_channel_user_item(premium_user, channel_deleted_livestreams_0)
    urls_to_notify_first_iteration = check_youtube(
        channel_deleted_livestreams_0, YouTubeVideo.get_new_videos(channel_deleted_livestreams_0, one_saved_livestream), YouTubeLivestream.get_new_livestreams(channel_deleted_livestreams_0, one_livestream))

    assert len(urls_to_notify_first_iteration) == 1
    assert channel_deleted_livestreams_0.deleted_livestreams == 0


@pytest.mark.django_db
def test_second_saved_livestream_if_channel_does_delete_its_livestreams_notification_for_premium_user(premium_user, channel_deleted_livestreams_1, videos, livestreams, one_livestream, one_saved_livestream):
    for video_id in videos:
        YouTubeVideo.objects.create(
            video_id=video_id,
            video_title=videos[video_id][0],
            is_saved_livestream=videos[video_id][1],
            channel=channel_deleted_livestreams_1
        )

    for livestream_id in livestreams:
        YouTubeLivestream.objects.create(
            livestream_id=livestream_id,
            livestream_title=livestreams[livestream_id],
            channel=channel_deleted_livestreams_1
        )

    create_channel_user_item(premium_user, channel_deleted_livestreams_1)
    urls_to_notify_first_iteration = check_youtube(
        channel_deleted_livestreams_1, YouTubeVideo.get_new_videos(channel_deleted_livestreams_1, one_saved_livestream), YouTubeLivestream.get_new_livestreams(channel_deleted_livestreams_1, one_livestream))
    for _ in range(settings.ITERATIONS_TO_SKIP + 1):
        urls_to_notify_final_iteration = check_youtube(
            channel_deleted_livestreams_1, YouTubeVideo.get_new_videos(channel_deleted_livestreams_1, one_saved_livestream), YouTubeLivestream.get_new_livestreams(channel_deleted_livestreams_1, one_livestream))

    assert len(urls_to_notify_first_iteration) == 0
    assert len(urls_to_notify_final_iteration) == 1
    assert channel_deleted_livestreams_1.deleted_livestreams == 0
