from django.conf import settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from bellify_bot.handlers.bot_handlers.utils import (
    add, get_upgrade_inline_keyboard, log_errors)
from bellify_bot.localization import localization
from bellify_bot.models import ChannelUserItem, Message, User
from twitch.utils import get_users_info, get_channel_title_from_url
from youtube.utils import get_channels_and_videos_info, scrape_id_by_url

from utils.general_utils import get_channel_url_type


@log_errors
def echo_handler(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(
        update.message.chat_id, update.message.from_user.username, False)
    user_text = update.message.text

    Message.get_or_create_message(u, user_text)

    try:
        echo_data = u.menu.split(f'{settings.SPLITTING_CHARACTER}')
    except Exception as e:
        echo_data = []

    if not all(data == '' for data in echo_data):
        if 'name' in echo_data:
            User.set_menu_field(u)
            channel_id, channel_type = echo_data[-2], echo_data[-1]
            add(channel_id, channel_type, update.message,
                u, user_text.lstrip())
    else:
        channel_type = get_channel_url_type(user_text)
        if channel_type:
            if channel_type == 'YouTube':
                channel_id = scrape_id_by_url(user_text)
                if channel_id:
                    _, _, channel_title = get_channels_and_videos_info(
                        [f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'])[0]
                else:
                    update.message.reply_text(
                        text=localization[u.language]['echo'][5],
                        parse_mode='HTML',)
                    return
            elif channel_type == 'Twitch':
                try:
                    channel_id, _, channel_title = get_users_info(
                        usernames=[get_channel_title_from_url(user_text)])[0]
                except IndexError as e:
                    update.message.reply_text(
                        text=localization[u.language]['echo'][5],
                        parse_mode='HTML',)
                    return
            if ChannelUserItem.is_user_subscribed_to_channel(u, channel_id):
                keyboard = [
                    [
                        InlineKeyboardButton(
                            '🗑️', callback_data=f'link{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}remove'),
                        InlineKeyboardButton(
                            '❌', callback_data=f'link{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}cancel')
                    ]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                if u.is_tutorial_finished:
                    update.message.reply_text(
                        text=localization[u.language]['echo'][1],
                        parse_mode='HTML',
                        disable_web_page_preview=True,
                        reply_markup=reply_markup)
                else:
                    update.message.reply_text(
                        text=localization[u.language]['help'][7],
                        parse_mode='HTML',
                        disable_web_page_preview=True,
                        reply_markup=reply_markup)
            elif u.status == 'B' and channel_type != 'YouTube':
                update.message.reply_text(
                    text=localization[u.language]['echo'][3],
                    parse_mode='HTML',
                    reply_markup=InlineKeyboardMarkup(
                        get_upgrade_inline_keyboard(u, 'premium'))
                )
            elif ChannelUserItem.get_count_by_user_and_channel(u, channel_type=channel_type) <= User.get_max_for_channel(u, channel_type=channel_type):
                keyboard = [
                    [
                        InlineKeyboardButton(
                            '✔️', callback_data=f'add{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}{channel_type}{settings.SPLITTING_CHARACTER}yes'),
                        InlineKeyboardButton(
                            '❌', callback_data=f'add{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}{channel_type}')
                    ]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                User.set_menu_field(u)

                if u.is_tutorial_finished:
                    update.message.reply_text(
                        text=f"{localization[u.language]['echo'][0][0]}<a href=\"{user_text}\">{channel_title}</a>{localization[u.language]['echo'][0][1]}",
                        parse_mode='HTML',
                        disable_web_page_preview=True,
                        reply_markup=reply_markup)
                else:
                    update.message.reply_text(
                        text=f"{localization[u.language]['help'][2][0]}<a href=\"{user_text}\">{channel_title}</a>{localization[u.language]['help'][2][1]}",
                        parse_mode='HTML',
                        disable_web_page_preview=True,
                        reply_markup=reply_markup)
            else:
                update.message.reply_text(
                    text=localization[u.language]['echo'][4],
                    parse_mode='HTML',
                    reply_markup=InlineKeyboardMarkup(get_upgrade_inline_keyboard(
                        u, mode='quota'))
                )
        else:
            pass