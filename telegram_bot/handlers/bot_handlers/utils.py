from datetime import datetime
from typing import Dict, List, Optional, Union

import telegram
import telegram_notification.tasks as tasks
from django.conf import settings
from telegram import InlineKeyboardButton, MessageEntity, Update
from youtube.models import Channel, ChannelUserItem
from youtube.utils import get_channel_title, get_last_video

from telegram_bot.models import User

from telegram_bot.localization import localization


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
def check_for_new_video(channel: Channel):
    new_video_title, new_video_url, new_upload_time = get_last_video(
        channel.channel_id)

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


# Return Inline keyboard regarding mode and command
def get_inline_keyboard(p: User, command: str, page_num: int, buttons_mode: Optional[str] = 'callback_data'):
    keyboard = []
    pagination_button_set = []

    channels = [ChannelUserItem.objects.filter(
        user=p)[i:i + settings.PAGINATION_SIZE] for i in range(0, len(ChannelUserItem.objects.filter(user=p)), settings.PAGINATION_SIZE)]

    if buttons_mode == 'url':
        for channel in channels[page_num]:
            keyboard.append([
                InlineKeyboardButton(
                    f'{channel.channel_title}', url=channel.channel.channel_url)
            ])
    else:
        for channel in channels[page_num]:
            keyboard.append([
                InlineKeyboardButton(
                    f'{channel.channel_title}', callback_data=f'{command}‽{channel.channel.channel_id}')
            ])

    pagination_button_set.append(InlineKeyboardButton(
        '❮', callback_data=f'{command}‽pagination‽{page_num - 1}')) if page_num - 1 >= 0 else None
    pagination_button_set.append(InlineKeyboardButton(
        '❯', callback_data=f'{command}‽pagination‽{page_num + 1}')) if page_num + 1 < len(channels) else None
    keyboard.append(
        pagination_button_set) if pagination_button_set else None

    return keyboard


@log_errors
def add(channel_id: str, update: Update, p: User, name: Optional[str] = None) -> None:
    video_title, video_url, upload_time = get_last_video(channel_id)
    channel_name = name if name else get_channel_title(
        channel_id)
    channel, _ = Channel.objects.get_or_create(
        channel_url=f'https://www.youtube.com/channel/{channel_id}',
        defaults={
            'title': channel_name,
            'channel_id': channel_id,
            'video_title': video_title,
            'video_url': video_url,
            'video_publication_date': datetime.strptime(upload_time, "%m/%d/%Y, %H:%M:%S")
        }
    )
    if not p in channel.users.all():
        if not ChannelUserItem.objects.filter(user=p, channel_title=channel_name).exists():
            ChannelUserItem.objects.create(
                user=p, channel=channel, channel_title=channel_name)
            try:
                update.callback_query.message.reply_text(
                    text=f"{localization[p.language]['add_command'][2][0]} {channel_name}{localization[p.language]['add_command'][2][1]} <a href=\"{video_url}\">{video_title}</a>",
                    parse_mode='HTML'
                )
            except:
                update.message.reply_text(
                    text=f"{localization[p.language]['add_command'][2][0]} {channel_name}{localization[p.language]['add_command'][2][1]} <a href=\"{video_url}\">{video_title}</a>",
                    parse_mode='HTML'
                )
            return
        else:
            try:
                update.callback_query.message.reply_text(
                    text=localization[p.language]['add_command'][3],
                    parse_mode='HTML'
                )
            except:
                update.message.reply_text(
                    text=localization[p.language]['add_command'][3],
                    parse_mode='HTML'
                )
    else:
        try:
            update.callback_query.message.reply_text(
                text=f"{localization[p.language]['add_command'][4]} <a href=\"{video_url}\">{video_title}</a>",
                parse_mode='HTML'
            )
        except:
            update.message.reply_text(
                text=f"{localization[p.language]['add_command'][4]} <a href=\"{video_url}\">{video_title}</a>",
                parse_mode='HTML'
            )


@log_errors
def remove(update: Update, p: User, name: str) -> None:
    item = ChannelUserItem.objects.get(user=p, channel_title=name)
    item.delete()
    update.callback_query.edit_message_text(
        text=localization[p.language]['remove_command'][2],
        parse_mode='HTML'
    )


@log_errors
def check(update: Update, p: User, name: str) -> None:
    item = ChannelUserItem.objects.get(user=p, channel_title=name)
    if not check_for_new_video(item.channel):
        update.callback_query.edit_message_text(
            text=f'{localization[p.language]["check_command"][3]} <a href=\"{item.channel.video_url}\">{item.channel.video_title}</a>',
            parse_mode='HTML'
        )
    else:
        update.callback_query.delete_message()


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
