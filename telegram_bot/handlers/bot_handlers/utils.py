from typing import Optional

import telegram_notification.tasks as tasks
from django.conf import settings
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice,
                      Message, ReplyKeyboardMarkup, Update)
from telegram_bot.localization import localization
from telegram_bot.models import ChannelUserItem, User
from twitch.models import TwitchChannel, TwitchChannelUserItem
from twitch.utils import (get_twitch_channel_info,
                          get_channel_url_from_title,
                          get_channels_title_and_is_live)
from youtube.models import YouTubeChannel, YouTubeChannelUserItem
from youtube.utils import (get_channels_and_videos_info,
                           get_channels_live_title_and_url, get_url_from_id)

from utils.keyboards import (_get_keyboard, _get_notification_reply_markup,
                             get_html_link, get_manage_inline_keyboard,
                             get_upgrade_inline_keyboard, log_errors)


# Checks for streams and alerts every premium user if there is one
@log_errors
def check_for_live_stream_twitch() -> None:
    channels = list(TwitchChannel.objects.filter(users__status='P'))
    channels_urls = [channel.channel_url for channel in channels]

    live_info = get_channels_title_and_is_live(channels_urls)

    for channel, live_info_item in zip(channels, live_info):
        live_title, is_live = live_info_item
        if live_title:
            if live_title != channel.live_title and is_live != channel.is_live:
                channel.live_title = live_title
                channel.is_live = True
                tasks.notify_users([item.user for item in TwitchChannelUserItem.objects.filter(
                    channel=channel, user__status='P')], channel_info={'id': channel.channel_id,
                                                                       'url': channel.channel_url,
                                                                       'title': channel.live_title}, live=True)
        else:
            channel.live_title = None
            channel.is_live = False
        channel.save()


# Checks for streams and alerts every premium user if there is one
@log_errors
def check_for_live_stream_youtube() -> None:
    channels = list(YouTubeChannel.objects.filter(users__status='P'))
    channels_live_urls = [
        f'https://www.youtube.com/channel/{channel.channel_id}/live' for channel in channels]
    live_info = get_channels_live_title_and_url(channels_live_urls)
    for channel, live_info_item, in zip(channels, live_info):
        live_title, live_url, _ = live_info_item
        if live_title and live_url:
            if live_title != channel.live_title and live_url != channel.live_url:
                channel.live_title = live_title
                channel.live_url = live_url
                channel.is_live = True
                tasks.notify_users([item.user for item in YouTubeChannelUserItem.objects.filter(
                    channel=channel, user__status='P')], channel_info={'id': channel.channel_id,
                                                                       'url': channel.live_url,
                                                                       'title': channel.live_title}, live=True)
        else:
            channel.live_title = None
            channel.live_url = None
            channel.is_live = False
        channel.save()


# Checks for new video and alerts every user if there is one
@log_errors
def check_for_new_video() -> None:
    channels_live_urls = []
    channels_with_new_video = []

    channels = list(YouTubeChannel.objects.all())
    channels_urls = [
        f'https://www.youtube.com/feeds/videos.xml?channel_id={channel.channel_id}' for channel in channels]

    video_info = get_channels_and_videos_info(
        channels_urls)

    for channel, video_info_item in zip(channels, video_info):
        video_title, video_url, _ = video_info_item
        if video_url != channel.video_url:
            channels_with_new_video.append(
                (channel, video_title, video_url))
            channels_live_urls.append(
                f'https://www.youtube.com/channel/{channel.channel_id}/live')

    live_info = get_channels_live_title_and_url(channels_live_urls)

    for channel_with_new_video, live_info_item in zip(channels_with_new_video, live_info):
        live_title, live_url, is_upcoming = live_info_item
        channel, video_title, video_url = channel_with_new_video
        if live_title and live_url:
            if live_title != channel.live_title and live_url != channel.live_url:
                channel.live_title = live_title
                channel.live_url = live_url
                channel.is_live = True
                tasks.notify_users([item.user for item in YouTubeChannelUserItem.objects.filter(
                    channel=channel, user__status='P')], channel_info={'id': channel.channel_id,
                                                                       'url': channel.live_url,
                                                                       'title': channel.live_title}, live=True)
        elif not is_upcoming:
            channel.video_title = video_title
            channel.video_url = video_url
            tasks.notify_users([item.user for item in YouTubeChannelUserItem.objects.filter(
                channel=channel)], channel_info={'id': channel.channel_id,
                                                 'url': channel.video_url,
                                                 'title': channel.video_title})
        channel.save()


# Checks channel url type and call add function accordingly
@log_errors
def add(channel_id: str, channel_type: str, message: Message, u: User, name: Optional[str] = None) -> None:
    if channel_type == 'YouTube':
        _add_youtube_channel(channel_id, message, u, name)
    elif channel_type == 'Twitch':
        _add_twitch_channel(channel_id, message, u, name)


# Adds Twitch channel to a given user
@log_errors
def _add_twitch_channel(channel_id: str, message: Message, u: User, name: Optional[str] = None) -> None:
    channel_url = get_channel_url_from_title(channel_id)

    if not TwitchChannel.objects.filter(channel_id=channel_id).exists():
        _, live_title, is_live = get_twitch_channel_info(
            channel_url)
    else:
        channel = TwitchChannel.objects.get(channel_id=channel_id)
        live_title, is_live = channel.live_title, channel.is_live

    channel_name = name if name else channel_id
    channel, _ = TwitchChannel.objects.get_or_create(
        channel_id=channel_id,
        channel_url=channel_url,
        live_title=live_title if is_live else None,
        is_live=is_live
    )

    if not u in channel.users.all():
        if not TwitchChannelUserItem.objects.filter(user=u, channel_title=channel_name).exists():
            TwitchChannelUserItem.objects.create(
                user=u, channel=channel, channel_title=channel_name)

            message.reply_text(
                text=f"{localization[u.language]['add'][1][0]} {channel_name if is_live else get_html_link(channel_url, channel_id)}{localization[u.language]['add'][1][2 if is_live else 3]} {get_html_link(channel_url, live_title) if is_live else ''}",
                parse_mode='HTML',
                reply_markup=_get_notification_reply_markup(
                    live_title if is_live else channel_id, channel_url)
            )
            if not u.is_tutorial_finished:
                message.reply_text(
                    text=localization[u.language]['help'][3],
                    parse_mode='HTML',
                    reply_markup=ReplyKeyboardMarkup(_get_keyboard(u.language))
                )
        else:
            message.reply_text(
                text=localization[u.language]['add'][2],
                parse_mode='HTML'
            )


# Adds YouTube channel to a given user
@log_errors
def _add_youtube_channel(channel_id: str, message: Message, u: User, name: Optional[str] = None) -> None:
    if not YouTubeChannel.objects.filter(channel_id=channel_id).exists():
        video_title, video_url, channel_title = get_channels_and_videos_info(
            [f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'])[0]
        live_title, live_url, is_upcoming = get_channels_live_title_and_url(
            [f'https://www.youtube.com/channel/{channel_id}/live'])[0]
        if video_url == live_url:
            video_title, video_url, channel_title = get_channels_and_videos_info(
                [f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'], 1)[0]
        if is_upcoming:
            live_title, live_url = None, None

    else:
        channel = YouTubeChannel.objects.get(channel_id=channel_id)
        video_title, video_url, channel_title, live_title, live_url = channel.video_title, channel.video_url, channel.title, channel.live_title, channel.live_url

    channel_name = name if name else channel_title
    channel, _ = YouTubeChannel.objects.get_or_create(
        channel_url=get_url_from_id(channel_id),
        channel_title=channel_title,
        video_title=video_title,
        video_url=video_url,
        live_title=live_title,
        live_url=live_url,
        is_live=True if live_title else False
    )

    if not u in channel.users.all():
        if not YouTubeChannelUserItem.objects.filter(user=u, channel_title=channel_title).exists():
            YouTubeChannelUserItem.objects.create(
                user=u, channel=channel, channel_title=channel_name)

            if not live_title:
                message.reply_text(
                    text=f"{localization[u.language]['add'][1][0]} {channel_name}{localization[u.language]['add'][1][1]} <a href=\"{video_url}\">{video_title}</a>",
                    parse_mode='HTML',
                    reply_markup=_get_notification_reply_markup(
                        video_title, video_url)
                )
            else:
                message.reply_text(
                    text=f"{localization[u.language]['add'][1][0]} {channel_name}{localization[u.language]['add'][1][2]} <a href=\"{live_url}\">{live_title}</a>",
                    parse_mode='HTML',
                    reply_markup=_get_notification_reply_markup(
                        live_title, live_url)
                )
            if not u.is_tutorial_finished:
                message.reply_text(
                    text=localization[u.language]['help'][3],
                    parse_mode='HTML',
                    reply_markup=ReplyKeyboardMarkup(_get_keyboard(u.language))
                )
        else:
            message.reply_text(
                text=localization[u.language]['add'][2],
                parse_mode='HTML'
            )


# Removes given channel user item
@log_errors
def remove(update: Update, u: User, channel: ChannelUserItem) -> None:
    channel.delete()
    manage(update, u, mode="remove")


# Mutes given channel user item
@log_errors
def mute(update: Update, u: User, channel: ChannelUserItem) -> None:
    ChannelUserItem.mute_channel(u, channel)
    manage(update, u, mode="mute")


# Returns Manage replies according to call situation
@log_errors
def manage(update: Update, u: User, mode: Optional[str] = "echo") -> None:
    keyboard = get_manage_inline_keyboard(u)

    if keyboard:
        reply_markup = InlineKeyboardMarkup(keyboard)

        if mode == "echo":
            update.message.reply_text(
                text=localization[u.language]["manage"][0] if u.is_tutorial_finished else localization[u.language]["help"][4],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            update.callback_query.edit_message_text(
                text=localization[u.language]["manage"][0] if u.is_tutorial_finished else localization[u.language]["help"][5],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            User.set_tutorial_state(
                u, True) if not u.is_tutorial_finished else None
    else:
        if mode == "echo":
            update.message.reply_text(
                text=localization[u.language]["manage"][1],
                parse_mode='HTML'
            )
        else:
            update.callback_query.edit_message_text(
                text=localization[u.language]["manage"][2],
                parse_mode='HTML'
            )


# First reply on Upgrade command
@log_errors
def upgrade(message: Message, u: User):
    message.reply_text(
        text=localization[u.language]["upgrade"][0],
        reply_markup=InlineKeyboardMarkup(get_upgrade_inline_keyboard(u)),
        parse_mode='HTML'
    )


# Reply on user invoice
@log_errors
def reply_invoice(update: Update, u: User, title: str, description: str, payload: str, buy_button_label: str, price: int, mode: Optional[str] = 'upgrade'):
    keyboard = [
        [
            InlineKeyboardButton(buy_button_label, pay=True)
        ],
        [
            InlineKeyboardButton(
                localization[u.language]['upgrade'][6], callback_data=f"upgrade{settings.SPLITTING_CHARACTER}back{settings.SPLITTING_CHARACTER}{mode}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.callback_query.message.reply_invoice(
        title=title,
        description=description,
        payload=payload,
        provider_token=settings.PROVIDER_TOKEN,
        currency=settings.CURRENCY,
        prices=[LabeledPrice(description[:-1], price)],
        reply_markup=reply_markup
    )
