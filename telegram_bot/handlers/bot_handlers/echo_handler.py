from django.conf import settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from telegram_bot.handlers.bot_handlers.utils import (add,
                                                      get_channel_url_type,
                                                      get_lang_inline_keyboard,
                                                      get_upgrade_inline_keyboard,
                                                      log_errors, manage,
                                                      upgrade)
from telegram_bot.localization import localization
from telegram_bot.models import ChannelUserItem, Message, User
from twitch.utils import is_twitch_channel_exists
from youtube.utils import scrape_id_by_url, get_channels_and_videos_info


@log_errors
def manage_reply_command_handler(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(
        update.message.chat_id, update.message.from_user.username, False)
    user_text = update.message.text

    Message.get_or_create_message(u, user_text)

    manage(update, u)


@log_errors
def language_reply_command_handler(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(
        update.message.chat_id, update.message.from_user.username, False)
    user_text = update.message.text

    Message.get_or_create_message(u, user_text)

    reply_markup = InlineKeyboardMarkup(get_lang_inline_keyboard())

    update.message.reply_text(
        text=localization[u.language]['language_command'][0],
        parse_mode='HTML',
        reply_markup=reply_markup)


@log_errors
def help_reply_command_handler(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(
        update.message.chat_id, update.message.from_user.username, False)
    user_text = update.message.text

    Message.get_or_create_message(u, user_text)

    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    localization[u.language]['help'][0][1], callback_data='tutorial'),
            ]
        ]
    )

    update.message.reply_text(
        text=localization[u.language]['help'][0][0],
        parse_mode='HTML',
        reply_markup=reply_markup)


@log_errors
def upgrade_reply_command_handler(update: Update, context: CallbackContext) -> None:
    u, _ = User.get_or_create_profile(
        update.message.chat_id, update.message.from_user.username, False)
    user_text = update.message.text

    Message.get_or_create_message(u, user_text)

    upgrade(update.message, u)


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
                _, _, channel_title = get_channels_and_videos_info(
                    [f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'])[0]
            elif channel_type == 'Twitch':
                channel_id = channel_title = is_twitch_channel_exists(
                    user_text)

            if channel_id:
                if ChannelUserItem.is_user_subscribed_to_channel(u, channel_id):
                    keyboard = [
                        [
                            InlineKeyboardButton(
                                '🗑️', callback_data=f'link{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}{channel_type}{settings.SPLITTING_CHARACTER}remove'),
                            InlineKeyboardButton(
                                '❌', callback_data=f'link{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}{channel_type}{settings.SPLITTING_CHARACTER}cancel')
                        ]
                    ]

                    reply_markup = InlineKeyboardMarkup(keyboard)

                    update.message.reply_text(
                        text=localization[u.language]['echo'][1],
                        parse_mode='HTML',
                        disable_web_page_preview=True,
                        reply_markup=reply_markup)
                elif u.status == 'B' and not channel_type in settings.FREE_CHANNELS_TYPES:
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
                            text=f"{localization[u.language]['echo'][0][0]} <a href=\"{user_text}\">{channel_title} </a>{localization[u.language]['echo'][0][1]}",
                            parse_mode='HTML',
                            disable_web_page_preview=True,
                            reply_markup=reply_markup)
                    else:
                        update.message.reply_text(
                            text=f"{localization[u.language]['help'][2][0]} <a href=\"{user_text}\">{channel_title} </a>{localization[u.language]['help'][2][1]}",
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
                update.message.reply_text(
                    text=localization[u.language]['echo'][5],
                    parse_mode='HTML',)
        else:
            pass
