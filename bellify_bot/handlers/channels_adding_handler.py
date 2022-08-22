from datetime import timedelta
from typing import Optional

from bellify_bot.localization import localization
from bellify_bot.models import User
from django.utils.timezone import now
from telegram import Message
from twitch.models import TwitchChannel, TwitchChannelUserItem
from twitch.utils import get_streams_info, get_users_info
from utils.general_utils import get_html_bold, get_html_link
from utils.keyboards import get_notification_reply_markup, log_errors
from youtube.models import (YouTubeChannel, YouTubeChannelUserItem,
                            YouTubeLivestream, YouTubeVideo)
from youtube.utils import (get_url_from_id, scrape_id_and_title_by_url,
                           scrape_last_videos, scrape_livesteams)


# Checks channel url type and call add function accordingly
@log_errors
def add(channel_id: str, channel_type: str, message: Message, user: User, name: Optional[str] = None) -> None:
    if 'YouTube' in channel_type:
        _add_youtube_channel(channel_id, message, user, name)
    elif 'Twitch' in channel_type:
        _add_twitch_channel(channel_id, message, user, name)


# Adds Twitch channel to a given user
@log_errors
def _add_twitch_channel(channel_id: str, message: Message, user: User, name: Optional[str] = None) -> None:
    channel: TwitchChannel

    def _get_twitch_channel_message(u: User, channel_url: str, channel_name: str, game_name: str, preview_url: str, is_live: bool) -> str:
        general = f"{localization[u.language]['add'][1][0]} "
        name = get_html_bold(channel_name) if is_live else get_html_link(
            channel_url, channel_name)
        is_streaming = localization[u.language]['add'][1][
            1 if is_live and not 'Just Chatting' in game_name and game_name else 2 if not is_live else 3]
        game = f" {localization[u.language]['add'][1][4]} {game_name+'.'}" if (
            is_live and not 'Just Chatting' in game_name) else ''
        thumb_href = f"{get_html_link(url=preview_url) if is_live else ''}"
        return f'{general}{name}{is_streaming}{game}{thumb_href}'

    if not TwitchChannel.is_channel_exists(channel_id):
        _, channel_login, channel_title = get_users_info(
            ids=[channel_id])[0]

        channel, _ = TwitchChannel.objects.update_or_create(
            channel_id=channel_id,
            channel_title=channel_title,
            channel_login=channel_login,
        )

        stream_data = get_streams_info([channel_id])
        if stream_data:
            live_title, game_name, thumbnail_url, is_live = list(
                *stream_data.values())
        else:
            live_title, game_name, thumbnail_url, is_live = None, None, None, False
    else:
        channel = TwitchChannel.objects.get(
            channel_id=channel_id)
        channel_title = channel.channel_title

        live_title, game_name, thumbnail_url, is_live = channel.live_title, channel.game_name, channel.thumbnail_url, channel.is_live

    channel_name = name if name else channel_title

    channel.update(live_title=live_title, game_name=game_name,
                   thumbnail_url=thumbnail_url, is_live=is_live)

    if not user in channel.users.all():
        if not TwitchChannelUserItem.objects.filter(user=user, channel_title=channel_name).exists():
            item = TwitchChannelUserItem.objects.create(
                user=user, channel=channel, channel_title=channel_name)

            message.reply_text(
                text=_get_twitch_channel_message(
                    user, channel.channel_url, item.message_title_and_type, game_name,
                    channel.channel_url if user.is_twitch_thumbnail_disabled else channel.preview_url, is_live),
                parse_mode='HTML',
                reply_markup=get_notification_reply_markup(
                    live_title if is_live else channel_name, channel.channel_url)
            )
            if not user.is_tutorial_finished:
                message.reply_text(
                    text=localization[user.language]['help'][3],
                    parse_mode='HTML',
                )
        else:
            message.reply_text(
                text=localization[user.language]['add'][2],
                parse_mode='HTML'
            )


# Adds YouTube channel to a given user
@log_errors
def _add_youtube_channel(channel_id: str, message: Message, user: User, name: Optional[str] = None) -> None:
    channel: YouTubeChannel

    def _get_youtube_channel_message(u: User, channel_name: str, url: str, is_live: bool) -> str:
        general = f"{localization[u.language]['add'][1][0]} "
        channel_name = get_html_bold(channel_name)
        is_streaming = localization[u.language]['add'][1][1 if not is_live else 3]
        href = f'{get_html_link(url=url)}'
        return f'{general}{channel_name}{is_streaming}{href}'

    if not YouTubeChannel.is_channel_exists(channel_id):
        _, channel_title = scrape_id_and_title_by_url(
            get_url_from_id(channel_id))

        channel, _ = YouTubeChannel.objects.update_or_create(
            channel_id=channel_id,
            channel_title=channel_title
        )

        videos = scrape_last_videos(channel_id)
        livestreams = scrape_livesteams(channel_id)

        videos_to_create = []
        livestreams_to_create = []

        for livestream_id in livestreams:
            livestreams_to_create.append(
                YouTubeLivestream(
                    livestream_id=livestream_id,
                    livestream_title=livestreams[livestream_id],
                    channel=channel
                )
            )

        for index, video_id in enumerate(videos):
            videos_to_create.append(
                YouTubeVideo(
                    added_at=now() - timedelta(seconds=index),
                    video_id=video_id,
                    video_title=videos[video_id][0],
                    published_at=videos[video_id][1],
                    channel=channel
                )
            )

        YouTubeVideo.objects.bulk_create(videos_to_create)
        YouTubeLivestream.objects.bulk_create(livestreams_to_create)

    else:
        channel = YouTubeChannel.objects.get(channel_id=channel_id)
        channel_title = channel.channel_title

    channel_name = name if name else channel_title

    if not user in channel.users.all():
        if not YouTubeChannelUserItem.objects.filter(user=user, channel_title=channel_title).exists():
            item = YouTubeChannelUserItem.objects.create(
                user=user, channel=channel, channel_title=channel_name)

            ongoing_livestream = channel.ongoing_livestream
            last_video = channel.last_video

            if ongoing_livestream and user.status == 'P':
                message.reply_text(
                    text=_get_youtube_channel_message(
                        user, item.message_title_and_type, ongoing_livestream.livestream_url, True),
                    parse_mode='HTML',
                    reply_markup=get_notification_reply_markup(
                        ongoing_livestream.livestream_title, ongoing_livestream.livestream_url)
                )
            elif last_video:
                message.reply_text(
                    text=_get_youtube_channel_message(
                        user, item.message_title_and_type, last_video.video_url, False),
                    parse_mode='HTML',
                    reply_markup=get_notification_reply_markup(
                        last_video.video_title, last_video.video_url)
                )
            if not user.is_tutorial_finished:
                message.reply_text(
                    text=localization[user.language]['help'][3],
                    parse_mode='HTML',
                )
        else:
            message.reply_text(
                text=localization[user.language]['add'][2],
                parse_mode='HTML'
            )
