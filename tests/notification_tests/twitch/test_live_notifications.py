import pytest
from bellify_bot.handlers.notification_handler import \
    get_notifications_urls_for_twitch
from django.conf import settings
from tests.utils import (create_twitch_channel_user_item, premium_user,
                         twitch_channel, twitch_livestreams,
                         twitch_livestreams_just_chatting)

from twitch.models import TwitchChannel


@pytest.mark.django_db
def test_channel_goes_live(premium_user, twitch_channel, twitch_livestreams):
    create_twitch_channel_user_item(premium_user, twitch_channel)
    live_notification_urls = get_notifications_urls_for_twitch(
        [twitch_channel], twitch_livestreams)

    twitch_channel.delete()

    assert len(live_notification_urls) == 1


@pytest.mark.django_db
def test_channel_goes_live_before_threshold_is_passed(premium_user, twitch_channel, twitch_livestreams):
    create_twitch_channel_user_item(premium_user, twitch_channel)
    _ = get_notifications_urls_for_twitch(
        [twitch_channel], twitch_livestreams)
    _ = get_notifications_urls_for_twitch([
        twitch_channel], {})
    live_notification_urls = get_notifications_urls_for_twitch(
        [twitch_channel], twitch_livestreams)

    twitch_channel.delete()

    assert len(live_notification_urls) == 0
    assert twitch_channel.live_title == list(*twitch_livestreams.values())[0]
    assert twitch_channel.is_threshold_passed == False


@pytest.mark.django_db
def test_notification_message_of_different_games(premium_user, twitch_channel, twitch_livestreams, twitch_livestreams_just_chatting):
    create_twitch_channel_user_item(premium_user, twitch_channel)
    live_notification_urls_normal_game = get_notifications_urls_for_twitch(
        [twitch_channel], twitch_livestreams)
    _ = get_notifications_urls_for_twitch(
        [twitch_channel], {})

    twitch_channel.live_end_datetime = None
    twitch_channel.save()

    live_notification_urls_just_chatting = get_notifications_urls_for_twitch(
        [twitch_channel], twitch_livestreams_just_chatting)

    twitch_channel.delete()

    assert 'streaming' not in live_notification_urls_just_chatting[0]
    assert 'live' in live_notification_urls_just_chatting[0]

    assert 'streaming' in live_notification_urls_normal_game[0]
    assert 'live' not in live_notification_urls_normal_game[0]
