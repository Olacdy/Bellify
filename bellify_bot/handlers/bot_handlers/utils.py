from typing import Optional

import bellify.tasks as tasks
from bellify_bot.localization import localization
from bellify_bot.models import ChannelUserItem, User
from django.conf import settings
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice,
                      Message, Update)
from twitch.models import TwitchChannel, TwitchChannelUserItem
from twitch.utils import (get_channel_url_from_title, get_streams_info,
                          get_streams_info_chunks_async, get_users_info)
from youtube.models import YouTubeChannel, YouTubeChannelUserItem
from youtube.utils import (get_channels_and_videos_info,
                           get_channels_live_title_and_url, get_url_from_id,
                           is_youtube_channel_url)

from utils.general_utils import get_html_link, get_html_bold, get_manage_message
from utils.keyboards import (get_manage_inline_keyboard,
                             get_notification_reply_markup,
                             get_upgrade_inline_keyboard, log_errors)


# Checks for streams and alerts every premium user if there is one
@log_errors
def check_for_live_stream_twitch() -> None:
    channels = list(TwitchChannel.objects.filter(users__status='P'))
    channels_ids = [channel.channel_id for channel in channels]
    channels_ids = [channels_ids[i * 100:(i + 1) * 100]
                    for i in range((len(channels_ids) + 100 - 1) // 100)]

    live_info = {stream_item[0]: stream_item[1:]
                 for stream_item in get_streams_info_chunks_async(channels_ids)}

    for channel in channels:
        if channel.channel_id in live_info:
            stream_data = live_info[channel.channel_id]
            if stream_data[0] != channel.live_title and stream_data[3] != channel.is_live:
                TwitchChannel.update_live_info(
                    channel, live_title=stream_data[0], game_name=stream_data[1], thumbnail_url=stream_data[2], is_live=stream_data[3])
                tasks.notify_users([item.user for item in TwitchChannelUserItem.objects.filter(
                    channel=channel, user__status='P')], channel_info={'id': channel.channel_id,
                                                                       'url': channel.channel_url,
                                                                       'title': channel.live_title,
                                                                       'game_name': channel.game_name,
                                                                       'thumbnail_url': channel.thumbnail_image.url}, is_live=True)
        else:
            TwitchChannel.update_live_info(channel)
        channel.save()


# Checks for streams and alerts every premium user if there is one
@ log_errors
def check_for_live_stream_youtube() -> None:
    channels = list(YouTubeChannel.objects.filter(users__status='P'))
    channels_live_urls = [
        f'https://www.youtube.com/channel/{channel.channel_id}/live' for channel in channels]

    live_info = get_channels_live_title_and_url(channels_live_urls)

    for channel, live_info_item, in zip(channels, live_info):
        live_title, live_url, is_upcoming = live_info_item
        if live_title and live_url and not is_youtube_channel_url(live_url):
            if live_title != channel.live_title and live_url != channel.live_url or is_upcoming != channel.is_upcoming:
                YouTubeChannel.update_live_info(
                    channel, live_title=live_title, live_url=live_url, is_upcoming=is_upcoming, is_live=True)
                if not is_upcoming:
                    tasks.notify_users([item.user for item in YouTubeChannelUserItem.objects.filter(
                        channel=channel, user__status='P')], channel_info={'id': channel.channel_id,
                                                                           'url': channel.live_url,
                                                                           'title': channel.live_title}, is_live=True)
        else:
            YouTubeChannel.update_live_info(channel)
        channel.save()


# Checks for new video and alerts every user if there is one
@ log_errors
def check_for_new_video_youtube() -> None:
    channels = list(YouTubeChannel.objects.all())
    channels_urls = [
        f'https://www.youtube.com/feeds/videos.xml?channel_id={channel.channel_id}' for channel in channels]

    video_info = get_channels_and_videos_info(
        channels_urls)

    for channel, video_info_item in zip(channels, video_info):
        video_title, video_url, _ = video_info_item
        old_video_title, old_video_url = channel.video_title, channel.video_url
        if channel.video_url != video_url and channel.live_url != video_url:
            YouTubeChannel.update_video_info(
                channel, video_title=video_title, video_url=video_url)
            if video_title != channel.old_video_title:
                tasks.notify_users([item.user for item in YouTubeChannelUserItem.objects.filter(
                    channel=channel)], channel_info={'id': channel.channel_id,
                                                     'url': channel.video_url,
                                                     'title': channel.video_title})
            YouTubeChannel.update_video_info(
                channel, old_video_title=old_video_title, old_video_url=old_video_url)
            channel.save()


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
    def _get_twitch_channel_message(u: User, channel_url: str, channel_name: str, game_name: str, thumbnail_url: str, is_live: bool) -> str:
        general = f"{localization[u.language]['add'][1][0]} "
        name = get_html_bold(channel_name) if is_live else get_html_link(
            channel_url, channel_name)
        is_streaming = localization[u.language]['add'][1][2 if is_live else 3]
        game = f" {localization[u.language]['add'][1][4]} {game_name+'.'}" if (
            is_live and not 'Just Chatting' in game_name) else ''
        thumb_href = f"{get_html_link(url=thumbnail_url) if is_live else ''}"
        return f"{general}{name}{is_streaming}{game}{thumb_href}"

    _, channel_login, channel_title = get_users_info(ids=[channel_id])[0]

    channel_url = get_channel_url_from_title(channel_title)

    if not TwitchChannel.objects.filter(channel_id=channel_id).exists():
        stream_data = get_streams_info([channel_id])
        if stream_data:
            _, live_title, game_name, thumbnail_url, is_live = stream_data[0]
        else:
            live_title, game_name, thumbnail_url, is_live = None, None, None, False
    else:
        channel = TwitchChannel.objects.get(channel_id=channel_id)
        live_title, game_name, thumbnail_url, is_live = channel.live_title, channel.game_name, channel.thumbnail_url, channel.is_live

    channel_name = name if name else channel_title
    channel, _ = TwitchChannel.objects.get_or_create(
        channel_id=channel_id,
        channel_title=channel_title,
        channel_login=channel_login,
        channel_url=channel_url,
        live_title=live_title,
        game_name=game_name,
        thumbnail_url=thumbnail_url,
        is_live=is_live
    )

    thumbnail_url = channel.thumbnail_image.url if thumbnail_url else None

    if not u in channel.users.all():
        if not TwitchChannelUserItem.objects.filter(user=u, channel_title=channel_name).exists():
            TwitchChannelUserItem.objects.create(
                user=u, channel=channel, channel_title=channel_name)

            message.reply_text(
                text=_get_twitch_channel_message(
                    u, channel_url, channel_name, game_name, thumbnail_url, is_live),
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
    def _get_youtube_channel_message(u: User, channel_name: str, url: str, is_live: bool) -> str:
        general = f"{localization[u.language]['add'][1][0]} "
        channel_name = get_html_bold(channel_name)
        is_streaming = localization[u.language]['add'][1][2 if is_live else 1]
        href = f"{get_html_link(url=url)}"
        return f"{general}{channel_name}{is_streaming}{href}"

    if not YouTubeChannel.objects.filter(channel_id=channel_id).exists():
        video_title, video_url, channel_title = get_channels_and_videos_info(
            [f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'])[0]
        live_title, live_url, is_upcoming = get_channels_live_title_and_url(
            [f'https://www.youtube.com/channel/{channel_id}/live'])[0]
        if video_url == live_url:
            video_title, video_url, channel_title = get_channels_and_videos_info(
                [f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'], 1)[0]
        if is_youtube_channel_url(live_url):
            live_title, live_url, is_upcoming = None, None, None
    else:
        channel = YouTubeChannel.objects.get(channel_id=channel_id)
        video_title, video_url, channel_title, live_title, live_url, is_upcoming = channel.video_title, channel.video_url, channel.channel_title, channel.live_title, channel.live_url, channel.is_upcoming

    channel_name = name if name else channel_title
    channel, _ = YouTubeChannel.objects.get_or_create(
        channel_id=channel_id,
        channel_url=get_url_from_id(channel_id),
        channel_title=channel_title,
        video_title=video_title,
        video_url=video_url,
        live_title=live_title,
        live_url=live_url,
        is_live=True if live_title else False,
        is_upcoming=is_upcoming
    )

    if not u in channel.users.all():
        if not YouTubeChannelUserItem.objects.filter(user=u, channel_title=channel_title).exists():
            YouTubeChannelUserItem.objects.create(
                user=u, channel=channel, channel_title=channel_name)

            if live_url and video_url == live_url:
                message.reply_text(
                    text=_get_youtube_channel_message(
                        u, channel_name, video_url, True),
                    parse_mode='HTML',
                    reply_markup=get_notification_reply_markup(
                        live_title, live_url)
                )
            else:
                message.reply_text(
                    text=_get_youtube_channel_message(
                        u, channel_name, video_url, False),
                    parse_mode='HTML',
                    reply_markup=get_notification_reply_markup(
                        video_title, video_url)
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
    channel.delete() if u.is_tutorial_finished else None
    manage(update, u, mode='remove', page_num=page_num)


# Mutes given channel user item
@ log_errors
def mute(update: Update, u: User, channel: ChannelUserItem, page_num: Optional[int] = 0) -> None:
    ChannelUserItem.mute_channel(u, channel)
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
            User.set_tutorial_state(
                u, True) if not u.is_tutorial_finished else None
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
        prices=[LabeledPrice(description[:-1], price - 1)],
        reply_markup=reply_markup
    )
