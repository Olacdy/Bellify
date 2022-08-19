import itertools
import urllib.parse
from typing import Dict, List, Optional, Tuple

from bellify_bot.localization import localization
from bellify_bot.models import ChannelUserItem, User
from django.conf import settings
from twitch.models import TwitchChannel, TwitchChannelUserItem
from twitch.utils import get_twitch_streams_info
from utils.general_utils import get_html_bold, get_html_link, send_messages
from utils.keyboards import get_notification_reply_markup, log_errors
from youtube.models import (YouTubeChannel, YouTubeChannelUserItem,
                            YouTubeLivestream, YouTubeVideo)
from youtube.utils import get_youtube_livestreams, get_youtube_videos


# Util function that returns url to notify users of twitch livestreams
@log_errors
def get_notifications_urls_for_twitch(channels: List[TwitchChannel], livestreams: Dict[str, Tuple[str, str, str, bool]]) -> List[str]:
    livestreams_notification_urls = []

    for channel in channels:
        if channel.channel_id in livestreams:
            stream_data = livestreams[channel.channel_id]
            if stream_data[3] != channel.is_live:
                channel.update(
                    live_title=stream_data[0], game_name=stream_data[1], thumbnail_url=stream_data[2], is_live=stream_data[3])
                if channel.is_threshold_passed:
                    livestreams_notification_urls.extend(get_urls_to_notify(users=[item.user for item in TwitchChannelUserItem.objects.filter(channel=channel)],
                                                                            channel_id=channel.channel_id, url=channel.channel_url, content_title=channel.live_title,
                                                                            game_name=channel.game_name, preview_url=channel.preview_url, is_live=True))
        else:
            channel.update()

    return livestreams_notification_urls


# Util function that returns url to notify users of youtube videos
@log_errors
def get_notifications_urls_for_youtube_videos(channels: List[YouTubeChannel], videos: List[Dict[str, Tuple[str, bool]]]) -> Tuple[List[str], List[str]]:
    videos_notification_urls_basic_users = []
    videos_notification_urls_premium_users = []

    for channel, channel_videos in zip(channels, videos):
        for video in YouTubeVideo.get_new_videos(channel, channel_videos):
            if not video.is_basic_notified:
                videos_notification_urls_basic_users.extend(get_urls_to_notify(users=[item.user for item in YouTubeChannelUserItem.objects.filter(
                    channel=channel, user__status='B')], channel_id=channel.channel_id, url=video.video_url,
                    content_title=video.video_title, is_reuploaded=video.is_reuploaded))
                video.notify_basic()

            if not video.is_premium_notified:
                videos_notification_urls_premium_users.extend(get_urls_to_notify(users=[item.user for item in YouTubeChannelUserItem.objects.filter(
                    channel=channel, user__status='P')], channel_id=channel.channel_id, url=video.video_url,
                    content_title=video.video_title, is_reuploaded=video.is_reuploaded,
                    is_ended_livestream=video.is_ended_livestream, is_might_be_deleted=channel.is_deleting_livestreams))
                video.notify_premium()

    return videos_notification_urls_basic_users, videos_notification_urls_premium_users


# Util function that returns url to notify users of youtube livestreams
@log_errors
def get_notifications_urls_for_youtube_livestreams(channels: YouTubeChannel, livestreams: List[Dict[str, str]]) -> List[str]:
    livestream_notification_urls = []

    for channel, channel_livestreams in zip(channels, livestreams):
        for livestream in YouTubeLivestream.get_new_livestreams(channel, channel_livestreams):
            if livestream.is_new:
                livestream_notification_urls.extend(get_urls_to_notify(users=[item.user for item in YouTubeChannelUserItem.objects.filter(
                    channel=channel, user__status='P')], channel_id=channel.channel_id, url=livestream.livestream_url,
                    content_title=livestream.livestream_title, is_live=True))
                livestream.notified()

    return livestream_notification_urls


# Checks for streams and alerts every premium user if there is one
@ log_errors
def check_twitch() -> None:
    channels: List[TwitchChannel] = TwitchChannel.get_channels_to_review()
    channels_ids = [channel.channel_id for channel in channels]
    channels_ids = [channels_ids[i * 100:(i + 1) * 100]
                    for i in range((len(channels_ids) + 100 - 1) // 100)]

    livestreams = {stream_item[0]: stream_item[1:]
                   for stream_item in get_twitch_streams_info(channels_ids)}

    livestream_notification_urls = get_notifications_urls_for_twitch(
        channels, livestreams)

    send_messages(livestream_notification_urls)


# Checks for livestreams and new videos and alerts users if the are some
@log_errors
def check_youtube() -> None:
    channels: List[YouTubeChannel] = YouTubeChannel.get_channels_to_review()
    channels_premium: List[YouTubeChannel] = YouTubeChannel.get_channels_to_review_premium(
    )

    videos = get_youtube_videos(
        [channel.channel_id for channel in channels])
    livestreams = get_youtube_livestreams(
        [channel.channel_id for channel in channels_premium])

    livestreams_notification_urls = get_notifications_urls_for_youtube_livestreams(
        channels, livestreams)

    videos_notification_urls_basic_users, videos_notification_urls_premium_users = get_notifications_urls_for_youtube_videos(
        channels, videos)

    send_messages(videos_notification_urls_basic_users +
                  videos_notification_urls_premium_users + livestreams_notification_urls)


# Function that handles users notifications
def get_urls_to_notify(users: List[User], channel_id: str, url: str, content_title: str, game_name: Optional[str] = None, preview_url: Optional[str] = None, is_reuploaded: Optional[bool] = False, is_live: Optional[bool] = False, is_ended_livestream: Optional[bool] = False, is_might_be_deleted: Optional[bool] = False) -> None:
    def _get_message(user: User, channel_title: str, url: str, game_name: Optional[str] = None, preview_url: Optional[str] = None, is_reuploaded: Optional[bool] = False, is_live: Optional[bool] = False, is_ended_livestream: Optional[bool] = False, is_might_be_deleted: Optional[bool] = False) -> str:
        channel_title = get_html_bold(channel_title)

        if is_live:
            notification = f" — {localization[user.language]['notification'][1] if not game_name or game_name == 'Just Chatting' else localization[user.language]['notification'][2]+' '+game_name+'!'}"
            href = f"{get_html_link(url=preview_url if preview_url and not user.is_twitch_thumbnail_disabled else url)}"
            return f"{channel_title}{notification}{href}"
        else:
            if is_reuploaded:
                notification = f" — {localization[user.language]['notification'][3]}"
            elif is_ended_livestream:
                notification = f" — {localization[user.language]['notification'][4]}{(' ' + localization[user.language]['notification'][5]) if is_might_be_deleted else ''}"
            else:
                notification = f" — {localization[user.language]['notification'][0]}"
            href = f"{get_html_link(url=url)}"
            return f"{channel_title}{notification}{href}"

    def _get_url(user_id: str, message: str, disable_notification: Optional[bool] = False, reply_markup: Optional[List[List[Dict]]] = None, parse_mode: Optional[str] = 'HTML') -> str:
        return f'https://api.telegram.org/bot{settings.TOKEN}/sendMessage?chat_id={user_id}&parse_mode={parse_mode}&text={message}&disable_notification={disable_notification}&reply_markup={urllib.parse.quote(reply_markup.to_json())}'

    return [_get_url(user_id=user.user_id,
                     message=_get_message(user=user, channel_title=item.message_title_and_type, url=url,
                                          game_name=game_name, preview_url=preview_url,
                                          is_reuploaded=is_reuploaded, is_live=is_live,
                                          is_ended_livestream=is_ended_livestream,
                                          is_might_be_deleted=is_might_be_deleted),
                     disable_notification=item.is_muted,
                     reply_markup=get_notification_reply_markup(
                         content_title, url)) for user, item in zip(users, [ChannelUserItem.get_channel_by_user_and_channel_id(user, channel_id) for user in users])]
