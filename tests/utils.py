import pytest
from bellify_bot.models import User
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now
from youtube.models import YouTubeChannel, YouTubeChannelUserItem
from twitch.models import TwitchChannel, TwitchChannelUserItem


def create_youtube_channel_user_item(user, channel):
    return YouTubeChannelUserItem.objects.create(
        user=user,
        channel=channel
    )


def create_twitch_channel_user_item(user, channel):
    return TwitchChannelUserItem.objects.create(
        user=user,
        channel=channel
    )


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
def twitch_channel():
    return TwitchChannel.objects.create(
        channel_id='40488774',
        channel_title='GGwpLanaya',
    )


@pytest.fixture()
def youtube_channel():
    return YouTubeChannel.objects.create(
        channel_id='UCcAd5Np7fO8SeejB1FVKcYw',
        channel_title='Best Ever Food Review Show',
    )


@pytest.fixture()
def youtube_channel_deleted_livestreams_0():
    return YouTubeChannel.objects.create(
        channel_id='UCcAd5Np7fO8SeejB1FVKcYw',
        channel_title='Best Ever Food Review Show',
        deleted_livestreams=0,
    )


@pytest.fixture()
def youtube_channel_deleted_livestreams_1():
    return YouTubeChannel.objects.create(
        channel_id='UCcAd5Np7fO8SeejB1FVKcYw',
        channel_title='Best Ever Food Review Show',
        deleted_livestreams=1,
    )


@pytest.fixture()
def twitch_livestreams():
    return {'40488774': ('Test_Livestream_Title', 'Test_Game_Name', 'https://static-cdn.jtvnw.net/previews-ttv/live_user_ggwplanaya-1280x720.jpg', True)}


@pytest.fixture()
def twitch_livestreams_just_chatting():
    return {'40488774': ('Test_Livestream_Title', 'Just Chatting', 'https://static-cdn.jtvnw.net/previews-ttv/live_user_ggwplanaya-1280x720.jpg', True)}


@pytest.fixture()
def youtube_videos():
    return {
        'test_video_id_6': ('Test Video Title 6', now() - relativedelta(hour=1)),
        'test_video_id_5': ('Test Video Title 5', now() - relativedelta(hour=2)),
        'test_video_id_4': ('Test Video Title 4', now() - relativedelta(hour=3)),
        'test_video_id_3': ('Test Video Title 3', now() - relativedelta(hour=4)),
        'test_video_id_2': ('Test Video Title 2', now() - relativedelta(hour=5)),
        'test_video_id_1': ('Test Video Title 1', now() - relativedelta(hour=6)),
    }


@pytest.fixture()
def youtube_livestreams():
    return {
        'test_livestream_id_2': 'Test Livestream Title 2',
        'test_livestream_id_1': 'Test Livestream Title 1',
    }


@pytest.fixture()
def youtube_one_livestream():
    return {
        'test_livestream_id_1': 'Test Livestream Title 1',
    }


@pytest.fixture()
def youtube_one_saved_livestream():
    return {
        'test_livestream_id_1': ('Test Livestream Title 1', now() - relativedelta(hour=1)),
        'test_video_id_6': ('Test Video Title 6', now() - relativedelta(hour=2)),
        'test_video_id_5': ('Test Video Title 5', now() - relativedelta(hour=3)),
        'test_video_id_4': ('Test Video Title 4', now() - relativedelta(hour=4)),
        'test_video_id_3': ('Test Video Title 3', now() - relativedelta(hour=5)),
        'test_video_id_2': ('Test Video Title 2', now() - relativedelta(hour=6)),
    }


@pytest.fixture()
def youtube_new_video():
    return {
        'test_video_id_7': ('Test Video Title 7', now() - relativedelta(minutes=1)),
        'test_video_id_6': ('Test Video Title 6', now() - relativedelta(hour=1)),
        'test_video_id_5': ('Test Video Title 5', now() - relativedelta(hour=2)),
        'test_video_id_4': ('Test Video Title 4', now() - relativedelta(hour=3)),
        'test_video_id_3': ('Test Video Title 3', now() - relativedelta(hour=4)),
        'test_video_id_2': ('Test Video Title 2', now() - relativedelta(hour=5)),
        'test_video_id_1': ('Test Video Title 1', now() - relativedelta(hour=6)),
    }


@pytest.fixture()
def youtube_new_video_threshold_passed():
    return {
        'test_video_id_7': ('Test Video Title 7', now() - relativedelta(hour=1)),
        'test_video_id_6': ('Test Video Title 6', now() - relativedelta(hour=1)),
        'test_video_id_5': ('Test Video Title 5', now() - relativedelta(hour=2)),
        'test_video_id_4': ('Test Video Title 4', now() - relativedelta(hour=3)),
        'test_video_id_3': ('Test Video Title 3', now() - relativedelta(hour=4)),
        'test_video_id_2': ('Test Video Title 2', now() - relativedelta(hour=5)),
        'test_video_id_1': ('Test Video Title 1', now() - relativedelta(hour=6)),
    }


@pytest.fixture()
def youtube_new_video_reupload():
    return {
        'test_video_id_7': ('Test Video Title 6', now() - relativedelta(hour=1)),
        'test_video_id_5': ('Test Video Title 5', now() - relativedelta(hour=2)),
        'test_video_id_4': ('Test Video Title 4', now() - relativedelta(hour=3)),
        'test_video_id_3': ('Test Video Title 3', now() - relativedelta(hour=4)),
        'test_video_id_2': ('Test Video Title 2', now() - relativedelta(hour=5)),
        'test_video_id_1': ('Test Video Title 1', now() - relativedelta(hour=6)),
    }


@pytest.fixture()
def youtube_new_video_last_hidden():
    return {
        'test_video_id_7': ('Test Video Title 7', now() - relativedelta(minutes=1)),
        'test_video_id_6': ('Test Video Title 6', now() - relativedelta(hour=1)),
        'test_video_id_5': ('Test Video Title 5', now() - relativedelta(hour=2)),
        'test_video_id_4': ('Test Video Title 4', now() - relativedelta(hour=3)),
        'test_video_id_3': ('Test Video Title 3', now() - relativedelta(hour=4)),
        'test_video_id_2': ('Test Video Title 2', now() - relativedelta(hour=5)),
    }


@pytest.fixture()
def youtube_new_videos_beginning_and_middle():
    return {
        'test_video_id_7': ('Test Video Title 7', now() - relativedelta(minutes=5)),
        'test_video_id_6': ('Test Video Title 6', now() - relativedelta(hour=1)),
        'test_video_id_5': ('Test Video Title 5', now() - relativedelta(hour=2)),
        'test_video_id_4': ('Test Video Title 4', now() - relativedelta(hour=3)),
        'test_video_id_8': ('Test Video Title 8', now() - relativedelta(minutes=15)),
        'test_video_id_3': ('Test Video Title 3', now() - relativedelta(hour=4)),
        'test_video_id_2': ('Test Video Title 2', now() - relativedelta(hour=5)),
        'test_video_id_1': ('Test Video Title 1', now() - relativedelta(hour=6)),
    }
