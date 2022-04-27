from datetime import datetime
from lib2to3.pgen2.token import OP
from typing import Dict, List, Optional, Union

import aiohttp
import telegram
import telegram_notification.tasks as tasks
from asgiref.sync import sync_to_async
from django.conf import settings
from fake_headers import Headers
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity, Update
from telegram_bot.localization import localization
from telegram_bot.models import User
from youtube.models import Channel, ChannelUserItem
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


# Checks for new video and alerts every user if there is one
async def check_for_new_video(channel: Channel):
    headers = Headers()

    async with aiohttp.ClientSession(cookies=settings.SESSION_CLIENT_COOKIES) as session:
        new_video_title, new_video_url, new_upload_time, _ = get_channel_and_video_info(
            headers, session, channel.channel_id)

        if new_video_url != channel.video_url:
            channel.video_title = new_video_title
            channel.video_url = new_video_url
            channel.video_publication_date = datetime.strptime(
                new_upload_time, "%m/%d/%Y, %H:%M:%S")
            channel.save()
            users = [item.user for item in ChannelUserItem.objects.filter(
                channel=channel)]
            tasks.notify_users(users, channel)
            return True
        else:
            return False


# Returns Manage inline keyboard
def get_manage_inline_keyboard(u: User, page_num: Optional[int] = 0) -> List:
    keyboard = []
    pagination_button_set = []

    channels = [ChannelUserItem.objects.filter(
        user=u)[i:i + settings.PAGINATION_SIZE] for i in range(0, len(ChannelUserItem.objects.filter(user=u)), settings.PAGINATION_SIZE)]

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


@log_errors
async def add(channel_id: str, update: Update, u: User, name: Optional[str] = None) -> None:
    def _is_user_subscribed(u: User, channel: Channel):
        return u in channel.users.all()

    def _is_channel_item_exists(u: User, channel_title):
        return ChannelUserItem.objects.filter(user=u, channel_title=channel_title).exists()

    headers = Headers()

    async with aiohttp.ClientSession(cookies=settings.SESSION_CLIENT_COOKIES) as session:
        video_title, video_url, upload_time, channel_title = await get_channel_and_video_info(
            headers, session, channel_id)
        channel_name = name if name else channel_title
        channel, _ = await sync_to_async(Channel.objects.get_or_create, thread_sensitive=True)(
            channel_url=f'https://www.youtube.com/channel/{channel_id}',
            defaults={
                'title': channel_title,
                'channel_id': channel_id,
                'video_title': video_title,
                'video_url': video_url,
                'video_publication_date': datetime.strptime(upload_time, "%m/%d/%Y, %H:%M:%S")
            }
        )
        if not await sync_to_async(_is_user_subscribed, thread_sensitive=True)(u, channel):
            if not await sync_to_async(_is_channel_item_exists, thread_sensitive=True)(u, channel_name):
                await sync_to_async(ChannelUserItem.objects.create,  thread_sensitive=True)(
                    user=u, channel=channel, channel_title=channel_name)
                try:
                    update.callback_query.message.reply_text(
                        text=f"{localization[u.language]['add_command'][2][0]} {channel_name}{localization[u.language]['add_command'][2][1]} <a href=\"{video_url}\">{video_title}</a>",
                        parse_mode='HTML'
                    )
                except:
                    update.message.reply_text(
                        text=f"{localization[u.language]['add_command'][2][0]} {channel_name}{localization[u.language]['add_command'][2][1]} <a href=\"{video_url}\">{video_title}</a>",
                        parse_mode='HTML'
                    )
                return
            else:
                try:
                    update.callback_query.message.reply_text(
                        text=localization[u.language]['add_command'][3],
                        parse_mode='HTML'
                    )
                except:
                    update.message.reply_text(
                        text=localization[u.language]['add_command'][3],
                        parse_mode='HTML'
                    )
        else:
            try:
                update.callback_query.message.reply_text(
                    text=f"{localization[u.language]['add_command'][4]} <a href=\"{video_url}\">{video_title}</a>",
                    parse_mode='HTML'
                )
            except:
                update.message.reply_text(
                    text=f"{localization[u.language]['add_command'][4]} <a href=\"{video_url}\">{video_title}</a>",
                    parse_mode='HTML'
                )


@log_errors
def remove(update: Update, u: User, name: str) -> None:
    item = ChannelUserItem.objects.get(user=u, channel_title=name)
    item.delete()
    manage(update, u, mode="remove")


@log_errors
def mute(update: Update, u: User, name: str) -> None:
    ChannelUserItem.set_muted(u, name)
    manage(update, u, mode="mute")


@log_errors
def check(update: Update, u: User, name: str) -> None:
    item = ChannelUserItem.objects.get(user=u, channel_title=name)
    if not check_for_new_video(item.channel):
        update.callback_query.edit_message_text(
            text=f'{localization[u.language]["check_command"][3]} <a href=\"{item.channel.video_url}\">{item.channel.video_title}</a>',
            parse_mode='HTML'
        )
    else:
        update.callback_query.delete_message()


@log_errors
def manage(update: Update, u: User, mode: Optional[str] = "echo") -> None:
    keyboard = get_manage_inline_keyboard(u)

    if keyboard:
        reply_markup = InlineKeyboardMarkup(keyboard)

        if mode == "echo":
            update.message.reply_text(
                text="Managing Channels",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            update.callback_query.edit_message_text(
                text="Managing Channels",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    else:
        if mode == "echo":
            update.message.reply_text(
                text="Sorry, but You have no added channels right now. Try to add one.",
                parse_mode='HTML'
            )
        else:
            update.callback_query.edit_message_text(
                text="Looks like You have deleted all of Your channels.",
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
