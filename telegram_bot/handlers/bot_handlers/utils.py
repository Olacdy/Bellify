from typing import Dict, List, Optional, Union

import telegram
import telegram_notification.tasks as tasks
from django.conf import settings
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, Message,
                      MessageEntity, Update)
from telegram_bot.localization import localization
from telegram_bot.models import User
from youtube.models import YoutubeChannel, YoutubeChannelUserItem
from youtube.utils import (get_channels_and_videos_info,
                           get_channels_live_title_and_url)


def log_errors(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = f'Exception occured {e}'
            print(error_message)
            raise e

    return inner


# Checks for streams and alerts every premium user if there is one
def check_for_live_stream_youtube() -> None:
    channels = list(YoutubeChannel.objects.filter(users__status='P'))
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
                tasks.notify_users([item.user for item in YoutubeChannelUserItem.objects.filter(
                    channel=channel, is_muted=False, user__status='P')], channel, True)
        else:
            channel.live_title = None
            channel.live_url = None
            channel.is_live = False
        channel.save()


# Checks for new video and alerts every user if there is one
def check_for_new_video() -> None:
    channels_live_urls = []
    channels_with_new_video = []

    channels = list(YoutubeChannel.objects.all())
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
                tasks.notify_users([item.user for item in YoutubeChannelUserItem.objects.filter(
                    channel=channel, is_muted=False, user__status='P')], channel, True)
        elif not is_upcoming:
            channel.video_title = video_title
            channel.video_url = video_url
            tasks.notify_users([item.user for item in YoutubeChannelUserItem.objects.filter(
                channel=channel, is_muted=False)], channel)
        channel.save()


# Returns Manage inline keyboard
def get_manage_inline_keyboard(u: User, page_num: Optional[int] = 0) -> List:
    keyboard = []
    pagination_button_set = []

    channels = [YoutubeChannelUserItem.objects.filter(
        user=u)[i:i + settings.PAGINATION_SIZE] for i in range(0, len(YoutubeChannelUserItem.objects.filter(user=u)), settings.PAGINATION_SIZE)]

    if channels:
        for channel in channels[page_num]:
            keyboard.append([
                InlineKeyboardButton(
                    f'{channel.channel_title}', url=channel.channel.channel_url),
                InlineKeyboardButton(
                    f'🔈' if channel.is_muted else f'🔊', callback_data=f'manage{settings.SPLITTING_CHARACTER}{channel.channel.channel_id}{settings.SPLITTING_CHARACTER}mute'),
                InlineKeyboardButton(
                    f'❌', callback_data=f'manage{settings.SPLITTING_CHARACTER}{channel.channel.channel_id}{settings.SPLITTING_CHARACTER}remove')
            ])

        pagination_button_set.append(InlineKeyboardButton(
            '❮', callback_data=f'pagination{settings.SPLITTING_CHARACTER}{page_num - 1}')) if page_num - 1 >= 0 else None
        pagination_button_set.append(InlineKeyboardButton(
            '❯', callback_data=f'pagination{settings.SPLITTING_CHARACTER}{page_num + 1}')) if page_num + 1 < len(channels) else None
        keyboard.append(
            pagination_button_set) if pagination_button_set else None

    return keyboard


# Returns Language inline keyboard
@log_errors
def get_lang_inline_keyboard(command: Optional[str] = 'lang') -> List:
    keyboard = [
        [
            InlineKeyboardButton(
                '🇬🇧', callback_data=f'{command}{settings.SPLITTING_CHARACTER}en'),
            InlineKeyboardButton(
                '🇷🇺', callback_data=f'{command}{settings.SPLITTING_CHARACTER}ru')
        ]
    ]

    return keyboard


# Adds Youtube channel to a given user
@log_errors
def add_youtube_channel(channel_id: str, message: Message, u: User, name: Optional[str] = None) -> None:
    if not YoutubeChannel.objects.filter(channel_id=channel_id).exists():
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
        channel = YoutubeChannel.objects.get(channel_id=channel_id)
        video_title, video_url, channel_title, live_title, live_url = channel.video_title, channel.video_url, channel.title, channel.live_title, channel.live_url

    channel_name = name if name else channel_title
    channel, _ = YoutubeChannel.objects.get_or_create(
        channel_url=f'https://www.youtube.com/channel/{channel_id}',
        defaults={
            'title': channel_title,
            'channel_id': channel_id,
            'video_title': video_title,
            'video_url': video_url,
            'live_title': live_title,
            'live_url': live_url,
            'is_live': True if live_title else False
        }
    )

    if not u in channel.users.all():
        if not YoutubeChannelUserItem.objects.filter(user=u, channel_title=channel_title).exists():
            YoutubeChannelUserItem.objects.create(
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
        else:
            message.reply_text(
                text=localization[u.language]['add'][2],
                parse_mode='HTML'
            )


@log_errors
def remove(update: Update, u: User, name: str) -> None:
    item = YoutubeChannelUserItem.objects.get(user=u, channel_title=name)
    item.delete()
    manage(update, u, mode="remove")


@log_errors
def mute(update: Update, u: User, name: str) -> None:
    YoutubeChannelUserItem.set_muted(u, name)
    manage(update, u, mode="mute")


@log_errors
def manage(update: Update, u: User, mode: Optional[str] = "echo") -> None:
    keyboard = get_manage_inline_keyboard(u)

    if keyboard:
        reply_markup = InlineKeyboardMarkup(keyboard)

        if mode == "echo":
            update.message.reply_text(
                text=localization[u.language]["manage"][0],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            update.callback_query.edit_message_text(
                text=localization[u.language]["manage"][0],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
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


# Sends message to user
def _send_message(
    user_id: Union[str, int],
    text: str,
    parse_mode: Optional[str] = 'HTML',
    reply_markup: Optional[List[List[Dict]]] = None,
    reply_to_message_id: Optional[int] = None,
    disable_web_page_preview: Optional[bool] = None,
    entities: Optional[List[MessageEntity]] = None,
    tg_token: str = settings.TOKEN,
) -> bool:
    bot = telegram.Bot(tg_token)
    try:
        m = bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            disable_web_page_preview=disable_web_page_preview,
            entities=entities,
        )
    except telegram.error.Unauthorized:
        print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
        User.objects.filter(user_id=user_id).update(is_blocked_bot=True)
        success = False
    else:
        success = True
        User.objects.filter(user_id=user_id).update(is_blocked_bot=False)
    return success


def _get_notification_reply_markup(title: str, url: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text=title, url=url)]
    ])
