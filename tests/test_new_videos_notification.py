import itertools

import pytest
from bellify_bot.handlers.bot_handlers.utils import get_urls_to_notify
from bellify_bot.models import User
from django.conf import settings
from youtube.models import YouTubeChannel, YouTubeChannelUserItem, YouTubeDeletedVideo, YouTubeVideo


def check_youtube_videos(channel, new_videos) -> None:
    video_notification_urls = []

    for video in new_videos:
        if video.is_new:
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
        video_notification_urls))


@pytest.fixture()
def basic_user():
    return User.objects.create(
        user_id='325066507',
        username='golovakanta',
    )


@pytest.fixture()
def channel():
    return YouTubeChannel.objects.create(
        channel_id='UCcAd5Np7fO8SeejB1FVKcYw',
        channel_title='Best Ever Food Review Show',
        channel_url='https://www.youtube.com/channel/UCcAd5Np7fO8SeejB1FVKcYw'
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
def one_new_video():
    return {
        'MHUnaXJqWF4': ('EXTREME African Seafood!!! WILD Tanzania Street Food in Dar es Salaam!!', False),
        'bol-_4NZjWE': ('Buffalo Placenta!! World’s Most Bizarre Vegan Food!!', False),
        'INJK-vTKPdg': ('The Surprising Noodle Vietnam Loves Most!! It’s Not Pho!!', False),
        '1H2l7dHq1fs': ('Blood Red Jellyfish!! EXTREME Vietnam Street Food!!', False),
        'FSogD7bAHF8': ('$1 VS $152 Filipino Lechon!! Manila’s Meat Masterpiece!!', False),
        'v0NNI5wS_GM': ('Filipino Street Food That Will Kill You!! Manila Heart Attack Tour!!', False),
        'VXjrCIcGZmw': ('Bizarre Filipino Food in Pampanga!! Pets, Pigs and Pests!!', False),
    }


@pytest.fixture()
def one_new_video_last_one_hidden():
    return {
        'MHUnaXJqWF4': ('EXTREME African Seafood!!! WILD Tanzania Street Food in Dar es Salaam!!', False),
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
def test_set_new_videos(basic_user, channel, videos, one_new_video):
    for video_id in videos:
        YouTubeVideo.objects.get_or_create(
            video_id=video_id,
            video_title=videos[video_id][0],
            is_saved_livestream=videos[video_id][1],
            channel=channel
        )

    create_channel_user_item(basic_user, channel)
    urls_to_notify = check_youtube_videos(
        channel, YouTubeVideo.get_new_videos(channel, one_new_video))

    assert f'https://api.telegram.org/bot{settings.TOKEN}/sendMessage?chat_id={basic_user.user_id}' in urls_to_notify[
        0] and 'MHUnaXJqWF4' in urls_to_notify[0] and len(urls_to_notify) == 1


@pytest.mark.django_db
def test_new_video_last_one_hidden(basic_user, channel, videos, one_new_video_last_one_hidden):
    for video_id in videos:
        YouTubeVideo.objects.get_or_create(
            video_id=video_id,
            video_title=videos[video_id][0],
            is_saved_livestream=videos[video_id][1],
            channel=channel
        )

    create_channel_user_item(basic_user, channel)
    urls_to_notify = check_youtube_videos(
        channel, YouTubeVideo.get_new_videos(channel, one_new_video_last_one_hidden))

    assert f'https://api.telegram.org/bot{settings.TOKEN}/sendMessage?chat_id={basic_user.user_id}' in urls_to_notify[
        0] and 'MHUnaXJqWF4' in urls_to_notify[0] and len(urls_to_notify) == 1 and len(YouTubeDeletedVideo.objects.all()) == 0


@pytest.mark.django_db
def test_new_video_gets_hidden(basic_user, channel, videos, one_new_video):
    for video_id in videos:
        YouTubeVideo.objects.get_or_create(
            video_id=video_id,
            video_title=videos[video_id][0],
            is_saved_livestream=videos[video_id][1],
            channel=channel
        )

    create_channel_user_item(basic_user, channel)
    YouTubeVideo.get_new_videos(channel, one_new_video)
    urls_to_notify = check_youtube_videos(
        channel, YouTubeVideo.get_new_videos(channel, videos))

    assert len(urls_to_notify) == 0 and YouTubeDeletedVideo.objects.all()[
        0].video_id == list(one_new_video.keys())[0]
