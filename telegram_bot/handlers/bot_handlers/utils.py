import asyncio
from typing import Dict, List, Optional, Union
import streamlink

import aiohttp
import telegram
import telegram_notification.tasks as tasks
from asgiref.sync import sync_to_async
from django.conf import settings
from fake_headers import Headers
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      MessageEntity, Update, Message)
from telegram_bot.localization import localization
from telegram_bot.models import User
from youtube.models import YoutubeChannel, YoutubeChannelUserItem
from youtube.utils import get_channel_and_video_info


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
async def check_for_live_stream_youtube() -> None:

    def _get_premium_not_muted_users(channel: YoutubeChannel) -> List[User]:
        return [item.user for item in YoutubeChannelUserItem.objects.filter(
            channel=channel, is_muted=False, user__status='P')]

    def _get_list_of_premium_channels() -> List[YoutubeChannel]:
        return list(YoutubeChannel.objects.filter(users__status='P'))

    channels = await sync_to_async(_get_list_of_premium_channels, thread_sensitive=True)()
    for channel in channels:
        print(channel)
        if len(streamlink.streams(f"https://www.youtube.com/channel/{channel.channel_id}/live")) > 0:
            channel.is_live = True
            await sync_to_async(tasks.notify_users, thread_sensitive=True)(await sync_to_async(
                _get_premium_not_muted_users, thread_sensitive=True)(channel), channel, True)
        else:
            channel.is_live = False
        await sync_to_async(channel.save, thread_sensitive=True)()


# Checks for new video and alerts every user if there is one
async def check_for_new_video() -> None:

    def _get_not_muted_users(channel: YoutubeChannel) -> List[User]:
        return [item.user for item in YoutubeChannelUserItem.objects.filter(
            channel=channel, is_muted=False)]

    def _get_list_of_channels() -> List[YoutubeChannel]:
        return list(YoutubeChannel.objects.all())

    async with aiohttp.ClientSession(cookies=settings.SESSION_CLIENT_COOKIES) as session:
        channels = await sync_to_async(_get_list_of_channels, thread_sensitive=True)()
        for channel in channels:
            await asyncio.sleep(settings.REQUESTS_DELAY)
            new_video_title, new_video_url, new_upload_time, _ = await get_channel_and_video_info(
                Headers(), session, channel.channel_id)
            if new_video_url != channel.video_url:
                channel.video_title = new_video_title
                channel.video_url = new_video_url
                channel.video_publication_date = new_upload_time
                await sync_to_async(channel.save, thread_sensitive=True)()
                await sync_to_async(tasks.notify_users, thread_sensitive=True)(await sync_to_async(
                    _get_not_muted_users, thread_sensitive=True)(channel), channel)


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
async def add_youtube_channel(channel_id: str, message: Message, u: User, name: Optional[str] = None) -> None:
    def _is_user_subscribed(u: User, channel: YoutubeChannel):
        return u in channel.users.all()

    def _is_channel_item_with_same_name_exists(u: User, channel_title: str):
        return YoutubeChannelUserItem.objects.filter(user=u, channel_title=channel_title).exists()

    def _is_channel_exists(channel_id: str):
        return YoutubeChannel.objects.filter(channel_id=channel_id).exists()

    def _get_channel_essentials(channel_id: str):
        channel = YoutubeChannel.objects.get(channel_id=channel_id)
        return channel.video_title, channel.video_url, channel.video_publication_date, channel.title

    def _get_video_reply_markup(video_title: str, video_url: str):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(text=video_title, url=video_url)]
        ])

    if not await sync_to_async(_is_channel_exists, thread_sensitive=True)(channel_id):
        async with aiohttp.ClientSession(cookies=settings.SESSION_CLIENT_COOKIES) as session:
            video_title, video_url, upload_time, channel_title = await get_channel_and_video_info(
                Headers(), session, channel_id)
    else:
        video_title, video_url, upload_time, channel_title = await sync_to_async(_get_channel_essentials, thread_sensitive=True)(channel_id)

    channel_name = name if name else channel_title
    channel, _ = await sync_to_async(YoutubeChannel.objects.get_or_create, thread_sensitive=True)(
        channel_url=f'https://www.youtube.com/channel/{channel_id}',
        defaults={
            'title': channel_title,
            'channel_id': channel_id,
            'video_title': video_title,
            'video_url': video_url,
            'video_publication_date': upload_time
        }
    )

    if not await sync_to_async(_is_user_subscribed, thread_sensitive=True)(u, channel):
        if not await sync_to_async(_is_channel_item_with_same_name_exists, thread_sensitive=True)(u, channel_name):
            await sync_to_async(YoutubeChannelUserItem.objects.create,  thread_sensitive=True)(
                user=u, channel=channel, channel_title=channel_name)

            message.reply_text(
                text=f"{localization[u.language]['add'][1][0]} {channel_name} {localization[u.language]['add'][1][1]} <a href=\"{video_url}\">{video_title}</a>",
                parse_mode='HTML',
                reply_markup=_get_video_reply_markup(
                    video_title, video_url)
            )
        else:
            message.reply_text(
                text=localization[u.language]['add'][2],
                parse_mode='HTML'
            )
    else:
        message.reply_text(
            text=f"{localization[u.language]['add'][3]} <a href=\"{video_url}\">{video_title}</a>",
            parse_mode='HTML',
            reply_markup=_get_video_reply_markup(
                video_title, video_url)
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


def _get_youtube_video_reply_markup(video_title: str, video_url: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text=video_title, url=video_url)]
    ])


def _get_youtube_live_markup(u: User, channel_id: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text=localization[u.language]['notification']
                              [2], url=f'https://www.youtube.com/channel/{channel_id}/live')]
    ])
