from django.conf import settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from telegram_bot.handlers.bot_handlers.utils import (add,
                                                      get_channel_url_type,
                                                      get_lang_inline_keyboard,
                                                      log_errors, manage,
                                                      upgrade)
from telegram_bot.localization import localization
from telegram_bot.models import ChannelUserItem, Message, User
from twitch.utils import is_twitch_channel_exists
from youtube.utils import scrape_id_by_url


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
        if user_text == localization[u.language]['commands']['manage_command_text']:
            manage(update, u)
        elif user_text == localization[u.language]['commands']['language_command_text']:
            reply_markup = InlineKeyboardMarkup(get_lang_inline_keyboard())

            update.message.reply_text(
                text=localization[u.language]['lang_start_command'][0],
                parse_mode='HTML',
                reply_markup=reply_markup)
        elif user_text == localization[u.language]['commands']['help_command_text']:
            update.message.reply_text(
                text=localization[u.language]['help'][0],
                parse_mode='HTML'
            )
        elif user_text == localization[u.language]['commands']['upgrade_command_text']:
            upgrade(update, u)
        elif channel_type:
            channel_id = scrape_id_by_url(
                user_text) if channel_type == 'YouTube' else is_twitch_channel_exists(user_text)

            if channel_id:
                if ChannelUserItem.is_user_subscribed_to_channel(u, channel_id):
                    keyboard = [
                        [
                            InlineKeyboardButton(
                                '🗑️', callback_data=f'echo{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}{channel_type}{settings.SPLITTING_CHARACTER}remove'),
                            InlineKeyboardButton(
                                '❌', callback_data=f'echo{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}{channel_type}{settings.SPLITTING_CHARACTER}cancel')
                        ]
                    ]

                    reply_markup = InlineKeyboardMarkup(keyboard)

                    update.message.reply_text(
                        text=localization[u.language]['echo'][1],
                        parse_mode='HTML',
                        reply_markup=reply_markup)
                elif ChannelUserItem.get_count_by_user_and_channel(u, channel_type=channel_type) <= User.get_max_for_channel(u, channel_type=channel_type):
                    keyboard = [
                        [
                            InlineKeyboardButton(
                                '✔️', callback_data=f'echo{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}{channel_type}{settings.SPLITTING_CHARACTER}yes'),
                            InlineKeyboardButton(
                                '❌', callback_data=f'echo{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}{channel_type}{settings.SPLITTING_CHARACTER}no')
                        ]
                    ]

                    reply_markup = InlineKeyboardMarkup(keyboard)

                    update.message.reply_text(
                        text=localization[u.language]['echo'][2],
                        parse_mode='HTML',
                        reply_markup=reply_markup)
                else:
                    update.message.reply_text(
                        text=localization[u.language]['echo'][4],
                        parse_mode='HTML'
                    )
            else:
                update.message.reply_text(
                    text=localization[u.language]['echo'][5],
                    parse_mode='HTML',)
        else:
            pass
