import pytest
from bellify_bot.models import User
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now
from youtube.models import YouTubeChannel, YouTubeChannelUserItem


def create_channel_user_item(user, channel):
    return YouTubeChannelUserItem.objects.create(
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
        'bol-_4NZjWE': ('Buffalo Placenta!! World’s Most Bizarre Vegan Food!!', now() - relativedelta(hour=1)),
        'INJK-vTKPdg': ('The Surprising Noodle Vietnam Loves Most!! It’s Not Pho!!', now() - relativedelta(hour=2)),
        '1H2l7dHq1fs': ('Blood Red Jellyfish!! EXTREME Vietnam Street Food!!', now() - relativedelta(hour=3)),
        'FSogD7bAHF8': ('$1 VS $152 Filipino Lechon!! Manila’s Meat Masterpiece!!', now() - relativedelta(hour=4)),
        'v0NNI5wS_GM': ('Filipino Street Food That Will Kill You!! Manila Heart Attack Tour!!', now() - relativedelta(hour=5)),
        'VXjrCIcGZmw': ('Bizarre Filipino Food in Pampanga!! Pets, Pigs and Pests!!', now() - relativedelta(hour=6)),
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
        'test_id_1': ('Test Livestream 1', now() - relativedelta(hour=1)),
        'bol-_4NZjWE': ('Buffalo Placenta!! World’s Most Bizarre Vegan Food!!', now() - relativedelta(hour=2)),
        'INJK-vTKPdg': ('The Surprising Noodle Vietnam Loves Most!! It’s Not Pho!!', now() - relativedelta(hour=3)),
        '1H2l7dHq1fs': ('Blood Red Jellyfish!! EXTREME Vietnam Street Food!!', now() - relativedelta(hour=4)),
        'FSogD7bAHF8': ('$1 VS $152 Filipino Lechon!! Manila’s Meat Masterpiece!!', now() - relativedelta(hour=5)),
        'v0NNI5wS_GM': ('Filipino Street Food That Will Kill You!! Manila Heart Attack Tour!!', now() - relativedelta(hour=6)),
    }


@pytest.fixture()
def one_new_video():
    return {
        'MHUnaXJqWF4': ('EXTREME African Seafood!!! WILD Tanzania Street Food in Dar es Salaam!!', now() - relativedelta(minutes=1)),
        'bol-_4NZjWE': ('Buffalo Placenta!! World’s Most Bizarre Vegan Food!!', now() - relativedelta(hour=1)),
        'INJK-vTKPdg': ('The Surprising Noodle Vietnam Loves Most!! It’s Not Pho!!', now() - relativedelta(hour=2)),
        '1H2l7dHq1fs': ('Blood Red Jellyfish!! EXTREME Vietnam Street Food!!', now() - relativedelta(hour=3)),
        'FSogD7bAHF8': ('$1 VS $152 Filipino Lechon!! Manila’s Meat Masterpiece!!', now() - relativedelta(hour=4)),
        'v0NNI5wS_GM': ('Filipino Street Food That Will Kill You!! Manila Heart Attack Tour!!', now() - relativedelta(hour=5)),
        'VXjrCIcGZmw': ('Bizarre Filipino Food in Pampanga!! Pets, Pigs and Pests!!', now() - relativedelta(hour=6)),
    }


@pytest.fixture()
def one_new_video_last_one_hidden():
    return {
        'MHUnaXJqWF4': ('EXTREME African Seafood!!! WILD Tanzania Street Food in Dar es Salaam!!', now() - relativedelta(minutes=1)),
        'bol-_4NZjWE': ('Buffalo Placenta!! World’s Most Bizarre Vegan Food!!', now() - relativedelta(hour=1)),
        'INJK-vTKPdg': ('The Surprising Noodle Vietnam Loves Most!! It’s Not Pho!!', now() - relativedelta(hour=2)),
        '1H2l7dHq1fs': ('Blood Red Jellyfish!! EXTREME Vietnam Street Food!!', now() - relativedelta(hour=3)),
        'FSogD7bAHF8': ('$1 VS $152 Filipino Lechon!! Manila’s Meat Masterpiece!!', now() - relativedelta(hour=4)),
        'v0NNI5wS_GM': ('Filipino Street Food That Will Kill You!! Manila Heart Attack Tour!!', now() - relativedelta(hour=5)),
    }


@pytest.fixture()
def one_new_video_in_the_beginning_and_one_in_the_middle():
    return {
        'test_id_1': ('Test Title 1', now() - relativedelta(minutes=5)),
        'bol-_4NZjWE': ('Buffalo Placenta!! World’s Most Bizarre Vegan Food!!', now() - relativedelta(hour=1)),
        'INJK-vTKPdg': ('The Surprising Noodle Vietnam Loves Most!! It’s Not Pho!!', now() - relativedelta(hour=2)),
        '1H2l7dHq1fs': ('Blood Red Jellyfish!! EXTREME Vietnam Street Food!!', now() - relativedelta(hour=3)),
        'MHUnaXJqWF4': ('EXTREME African Seafood!!! WILD Tanzania Street Food in Dar es Salaam!!', now() - relativedelta(hour=3)),
        'FSogD7bAHF8': ('$1 VS $152 Filipino Lechon!! Manila’s Meat Masterpiece!!', now() - relativedelta(hour=4)),
        'v0NNI5wS_GM': ('Filipino Street Food That Will Kill You!! Manila Heart Attack Tour!!', now() - relativedelta(hour=5)),
        'VXjrCIcGZmw': ('Bizarre Filipino Food in Pampanga!! Pets, Pigs and Pests!!', now() - relativedelta(hour=6)),
    }
