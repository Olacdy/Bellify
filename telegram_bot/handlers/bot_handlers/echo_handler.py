import asyncio

from django.conf import settings
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      KeyboardButton, ReplyKeyboardMarkup, Update)
from telegram.ext import CallbackContext
from telegram_bot.handlers.bot_handlers.utils import (
    add, get_lang_inline_keyboard, manage, log_errors)
from telegram_bot.localization import localization
from telegram_bot.models import Message, User
from youtube.models import Channel, ChannelUserItem
from youtube.utils import is_channel_url, scrape_id_by_url


manage_command_text = "⚙️Manage channels⚙️"
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
            asyncio.run(add(channel_id, update, u, user_text.lstrip()))
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
                text=localization[u.language]['help_command'][0],
                parse_mode='HTML'
            )
        elif user_text == upgrade_command_text:
            pass
        elif is_channel_url(user_text):
            channel_id = scrape_id_by_url(user_text)
            channel = Channel.objects.filter(channel_url=user_text).first()
            if ChannelUserItem.objects.filter(user=u, channel=channel).exists():
                keyboard = [
                    [
                        InlineKeyboardButton(
                            'Check' if u.language == 'en' else 'Проверить', callback_data=f'echo{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}check'),
                        InlineKeyboardButton(
                            'Remove' if u.language == 'en' else 'Удалить', callback_data=f'echo{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}remove')
                    ]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                update.message.reply_text(
                    text=localization[u.language]['echo'][2],
                    parse_mode='HTML',
                    reply_markup=reply_markup)
            else:
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
                    text=localization[u.language]['echo'][3],
                    parse_mode='HTML',
                    reply_markup=reply_markup)
        else:
            pass
