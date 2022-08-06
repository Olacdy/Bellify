import time
from typing import List, Optional

import bellify.tasks as tasks
from bellify_bot.localization import localization
from bellify_bot.models import ChannelUserItem, User
from django.conf import settings
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice,
                      Message, Update)
from twitch.models import TwitchChannel, TwitchChannelUserItem
from twitch.utils import (get_channel_url_from_title, get_streams_info,
                          get_twitch_streams_info, get_users_info)
from youtube.models import (YouTubeChannel, YouTubeChannelUserItem, YouTubeEndedLivestream,
                            YouTubeLivestream, YouTubeVideo)
from youtube.utils import (get_url_from_id, get_youtube_livestreams,
                           get_youtube_videos, scrape_id_and_title_by_url,
                           scrape_last_videos, scrape_livesteams)

from utils.general_utils import (get_html_bold, get_html_link,
                                 get_manage_message)
from utils.keyboards import (get_manage_inline_keyboard,
                             get_notification_reply_markup,
                             get_upgrade_inline_keyboard, log_errors)


# Checks for streams and alerts every premium user if there is one
@log_errors
def check_twitch() -> None:
    channels: List[TwitchChannel] = list(TwitchChannel.objects.all())
    channels_ids = [channel.channel_id for channel in channels]
    channels_ids = [channels_ids[i * 100:(i + 1) * 100]
                    for i in range((len(channels_ids) + 100 - 1) // 100)]

    live_info = {stream_item[0]: stream_item[1:]
                 for stream_item in get_twitch_streams_info(channels_ids)}

    for channel in channels:
        if channel.channel_id in live_info:
            stream_data = live_info[channel.channel_id]
            if stream_data[3] != channel.is_live and channel.is_live == False:
                channel.update_live_info(
                    live_title=stream_data[0], game_name=stream_data[1], thumbnail_url=stream_data[2], is_live=stream_data[3])
                tasks.notify_users([item.user for item in TwitchChannelUserItem.objects.filter(
                    channel=channel)], content_info={'id': channel.channel_id,
                                                     'url': channel.channel_url,
                                                     'title': channel.live_title,
                                                     'game_name': channel.game_name,
                                                     'preview_url': channel.preview_url,
                                                     'is_live': True})
        else:
            channel.update_live_info()


# Checks for livestreams and new videos and alerts users if the are some
@ log_errors
def check_youtube() -> None:
    channels: List[YouTubeChannel] = list(YouTubeChannel.objects.all())
    channels_premium: List[YouTubeChannel] = list(
        YouTubeChannel.objects.filter(users__status='P'))

    channels_videos_info = get_youtube_videos(
        [channel.channel_id for channel in channels])
    channels_livestreams_info = get_youtube_livestreams(
        [channel.channel_id for channel in channels_premium])

    if channels_livestreams_info:
        for channel_premium, channel_livestreams_info_item in zip(channels_premium, channels_livestreams_info):
            for livestream in YouTubeLivestream.get_new_livestreams(channel_premium, channel_livestreams_info_item):
                if not livestream.is_notified:
                    tasks.notify_users([item.user for item in YouTubeChannelUserItem.objects.filter(
                        channel=channel_premium)], content_info={'id': channel_premium.channel_id,
                                                                 'url': livestream.livestream_url,
                                                                 'title': livestream.livestream_title,
                                                                 'is_live': True})
                    livestream.notified()

    if channels_videos_info:
        for channel, channel_videos_info_item in zip(channels, channels_videos_info):
            for video in YouTubeVideo.get_new_videos(channel, channel_videos_info_item):
                if not video.is_notified:
                    if video.is_saved_livestream and not video.is_able_to_notify:
                        video.skip_iteration()
                    else:
                        tasks.notify_users([item.user for item in YouTubeChannelUserItem.objects.filter(
                            channel=channel)], content_info={'id': channel.channel_id,
                                                             'url': video.video_url,
                                                             'title': video.video_title,
                                                             'is_saved_livestream': video.is_saved_livestream and YouTubeEndedLivestream.is_in_ended_stream(channel_premium, video),
                                                             'might_be_deleted': channel.is_deleting_livestreams,
                                                             'is_reuploaded': video.is_reuploaded})
                        video.notified()


# Checks channel url type and call add function accordingly
@ log_errors
def add(channel_id: str, channel_type: str, message: Message, u: User, name: Optional[str] = None) -> None:
    if 'YouTube' in channel_type:
        _add_youtube_channel(channel_id, message, u, name)
    elif 'Twitch' in channel_type:
        _add_twitch_channel(channel_id, message, u, name)


# Adds Twitch channel to a given user
@ log_errors
def _add_twitch_channel(channel_id: str, message: Message, u: User, name: Optional[str] = None) -> None:
    channel: TwitchChannel

    def _get_twitch_channel_message(u: User, channel_url: str, channel_name: str, game_name: str, preview_url: str, is_live: bool) -> str:
        general = f"{localization[u.language]['add'][1][0]} "
        name = get_html_bold(channel_name) if is_live else get_html_link(
            channel_url, channel_name)
        is_streaming = localization[u.language]['add'][1][
            1 if is_live and not 'Just Chatting' in game_name else 2 if not is_live else 3]
        game = f" {localization[u.language]['add'][1][4]} {game_name+'.'}" if (
            is_live and not 'Just Chatting' in game_name) else ''
        thumb_href = f"{get_html_link(url=preview_url) if is_live else ''}"
        return f'{general}{name}{is_streaming}{game}{thumb_href}'

    if not TwitchChannel.objects.filter(channel_id=channel_id).exists():
        _, channel_login, channel_title = get_users_info(
            ids=[channel_id])[0]
        channel_url = get_channel_url_from_title(channel_title)

        channel, _ = TwitchChannel.objects.get_or_create(
            channel_id=channel_id,
            channel_title=channel_title,
            channel_login=channel_login,
            channel_url=channel_url
        )

        stream_data = get_streams_info([channel_id])
        if stream_data:
            _, live_title, game_name, thumbnail_url, is_live = stream_data[0]
        else:
            live_title, game_name, thumbnail_url, is_live = None, None, None, False
    else:
        channel = TwitchChannel.objects.get(
            channel_id=channel_id)
        channel_title, channel_url = channel.channel_title, get_channel_url_from_title(
            channel.channel_title)

        live_title, game_name, thumbnail_url, is_live = channel.live_title, channel.game_name, channel.thumbnail_url, channel.is_live

    channel_name = name if name else channel_title

    channel.update_live_info(live_title=live_title, game_name=game_name,
                             thumbnail_url=thumbnail_url, is_live=is_live)

    if not u in channel.users.all():
        if not TwitchChannelUserItem.objects.filter(user=u, channel_title=channel_name).exists():
            item = TwitchChannelUserItem.objects.create(
                user=u, channel=channel, channel_title=channel_name)

            message.reply_text(
                text=_get_twitch_channel_message(
                    u, channel_url, item.message_title_and_type, game_name, channel.channel_url if u.is_twitch_thumbnail_disabled else channel.preview_url, is_live),
                parse_mode='HTML',
                reply_markup=get_notification_reply_markup(
                    live_title if is_live else channel_name, channel_url)
            )
            if not u.is_tutorial_finished:
                message.reply_text(
                    text=localization[u.language]['help'][3],
                    parse_mode='HTML',
                )
        else:
            message.reply_text(
                text=localization[u.language]['add'][2],
                parse_mode='HTML'
            )


# Adds YouTube channel to a given user
@ log_errors
def _add_youtube_channel(channel_id: str, message: Message, u: User, name: Optional[str] = None) -> None:
    channel: YouTubeChannel

    def _get_youtube_channel_message(u: User, channel_name: str, url: str, is_live: bool) -> str:
        general = f"{localization[u.language]['add'][1][0]} "
        channel_name = get_html_bold(channel_name)
        is_streaming = localization[u.language]['add'][1][1 if not is_live else 3]
        href = f'{get_html_link(url=url)}'
        return f'{general}{channel_name}{is_streaming}{href}'

    if not YouTubeChannel.objects.filter(channel_id=channel_id).exists():
        channel_url = get_url_from_id(channel_id)
        _, channel_title = scrape_id_and_title_by_url(channel_url)

        channel, _ = YouTubeChannel.objects.get_or_create(
            channel_id=channel_id,
            channel_url=channel_url,
            channel_title=channel_title
        )

        videos = scrape_last_videos(channel_id)
        livestreams = scrape_livesteams(channel_id)

        for livestream in livestreams:
            YouTubeLivestream.objects.get_or_create(
                livestream_id=livestream[0],
                livestream_title=livestream[1],
                channel=channel
            )

        for video in videos:
            YouTubeVideo.objects.get_or_create(
                video_id=video[0],
                video_title=video[1],
                is_saved_livestream=video[2],
                channel=channel
            )
    else:
        channel = YouTubeChannel.objects.get(channel_id=channel_id)
        channel_title = channel.channel_title

    channel_name = name if name else channel_title

    if not u in channel.users.all():
        if not YouTubeChannelUserItem.objects.filter(user=u, channel_title=channel_title).exists():
            item = YouTubeChannelUserItem.objects.create(
                user=u, channel=channel, channel_title=channel_name)

            ongoing_livestream = channel.ongoing_livestream
            last_video = channel.last_video

            if ongoing_livestream and u.status == 'P':
                message.reply_text(
                    text=_get_youtube_channel_message(
                        u, item.message_title_and_type, ongoing_livestream.livestream_url, True),
                    parse_mode='HTML',
                    reply_markup=get_notification_reply_markup(
                        ongoing_livestream.livestream_title, ongoing_livestream.livestream_url)
                )
            else:
                message.reply_text(
                    text=_get_youtube_channel_message(
                        u, item.message_title_and_type, last_video.video_url, False),
                    parse_mode='HTML',
                    reply_markup=get_notification_reply_markup(
                        last_video.video_title, last_video.video_url)
                )
            if not u.is_tutorial_finished:
                message.reply_text(
                    text=localization[u.language]['help'][3],
                    parse_mode='HTML',
                )
        else:
            message.reply_text(
                text=localization[u.language]['add'][2],
                parse_mode='HTML'
            )


# Removes given channel user item
@ log_errors
def remove(update: Update, u: User, channel: ChannelUserItem, page_num: Optional[int] = 0) -> None:
    channel.delete() if u.is_tutorial_finished and channel else None
    manage(update, u, mode='remove', page_num=page_num)


# Mutes given channel user item
@ log_errors
def mute(update: Update, u: User, channel: ChannelUserItem, page_num: Optional[int] = 0) -> None:
    channel.mute_channel() if channel else None
    manage(update, u, mode='mute', page_num=page_num)


# Returns Manage replies according to call situation
@ log_errors
def manage(update: Update, u: User, mode: Optional[str] = 'echo', page_num: Optional[int] = 0) -> None:
    keyboard = get_manage_inline_keyboard(u, page_num=page_num)

    if keyboard:
        reply_markup = InlineKeyboardMarkup(keyboard)

        if 'echo' in mode:
            update.message.reply_text(
                text=get_manage_message(u, mode='echo'),
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            update.callback_query.edit_message_text(
                text=get_manage_message(u),
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            u.set_tutorial_state(True) if not u.is_tutorial_finished else None
    else:
        if 'echo' in mode:
            update.message.reply_text(
                text=localization[u.language]['manage'][1],
                parse_mode='HTML'
            )
        else:
            update.callback_query.edit_message_text(
                text=localization[u.language]['manage'][2],
                parse_mode='HTML'
            )


# First reply on Upgrade command
@ log_errors
def upgrade(message: Message, u: User):
    message.reply_text(
        text=localization[u.language]['upgrade'][0],
        reply_markup=InlineKeyboardMarkup(get_upgrade_inline_keyboard(u)),
        parse_mode='HTML'
    )


# Reply on user invoice
@ log_errors
def reply_invoice(update: Update, u: User, title: str, description: str, payload: str, buy_button_label: str, price: int, mode: Optional[str] = 'upgrade'):
    keyboard = [
        [
            InlineKeyboardButton(buy_button_label, pay=True)
        ],
        [
            InlineKeyboardButton(
                localization[u.language]['upgrade'][6], callback_data=f'upgrade{settings.SPLITTING_CHARACTER}back{settings.SPLITTING_CHARACTER}{mode}')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.callback_query.message.reply_invoice(
        title=title,
        description=description,
        payload=payload,
        provider_token=settings.PROVIDER_TOKEN,
        currency=settings.CURRENCY,
        prices=[LabeledPrice(description[:-1], (price - 1)
                             if not repr(price)[-1] == '5' else price)],
        reply_markup=reply_markup
    )
