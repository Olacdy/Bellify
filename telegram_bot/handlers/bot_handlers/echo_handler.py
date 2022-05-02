import asyncio

from django.conf import settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from telegram_bot.handlers.bot_handlers.utils import (add_youtube_channel,
                                                      get_lang_inline_keyboard,
                                                      log_errors, manage)
from telegram_bot.localization import localization
from telegram_bot.models import Message, User
from youtube.models import YoutubeChannel, YoutubeChannelUserItem
from youtube.utils import get_channel_url_type, scrape_id_by_url

manage_command_text = "⚙️Manage Channels⚙️"
language_command_text = "🗣️Language🗣️"
help_command_text = "📑Help📑"
upgrade_command_text = "⚡Upgrade⚡"


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
            channel_id = u.menu.split(f'{settings.SPLITTING_CHARACTER}')[-1]
            asyncio.run(add_youtube_channel(
                channel_id, update.message, u, user_text.lstrip()))
    else:
        if user_text == manage_command_text:
            manage(update, u)
        elif user_text == language_command_text:
            reply_markup = InlineKeyboardMarkup(get_lang_inline_keyboard())

            update.message.reply_text(
                text=localization[u.language]['lang_start_command'][0],
                parse_mode='HTML',
                reply_markup=reply_markup)
        elif user_text == help_command_text:
            update.message.reply_text(
                text=localization[u.language]['help'][0],
                parse_mode='HTML'
            )
        elif user_text == upgrade_command_text:
            pass
        elif get_channel_url_type(user_text) == 'Youtube':
            channel_id = scrape_id_by_url(user_text)
            channel = YoutubeChannel.objects.filter(
                channel_id=channel_id).first()

            if YoutubeChannelUserItem.objects.filter(user=u, channel=channel).exists():
                keyboard = [
                    [
                        InlineKeyboardButton(
                            'Remove' if u.language == 'en' else 'Удалить', callback_data=f'echo{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}remove'),
                        InlineKeyboardButton(
                            'Cancel' if u.language == 'en' else 'Отмена', callback_data=f'echo{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}cancel')
                    ]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                update.message.reply_text(
                    text=localization[u.language]['echo'][1],
                    parse_mode='HTML',
                    reply_markup=reply_markup)
            elif YoutubeChannelUserItem.objects.filter(user=u).count() + 1 <= u.max_youtube_channels_number:
                keyboard = [
                    [
                        InlineKeyboardButton(
                            'Yes' if u.language == 'en' else 'Да', callback_data=f'echo{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}yes'),
                        InlineKeyboardButton(
                            'No' if u.language == 'en' else 'Нет', callback_data=f'echo{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}no')
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
        # TODO make Twitch channel functionality
        elif get_channel_url_type(user_text) == 'Twitch':
            pass
        else:
            pass
