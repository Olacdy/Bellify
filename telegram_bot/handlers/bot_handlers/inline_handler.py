import asyncio

from django.conf import settings
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      KeyboardButton, ReplyKeyboardMarkup, Update)
from telegram.ext import CallbackContext
from telegram_bot.handlers.bot_handlers.echo_handler import (
    help_command_text, language_command_text, manage_command_text,
    upgrade_command_text)
from telegram_bot.handlers.bot_handlers.utils import (
    add, check, get_manage_inline_keyboard, log_errors, mute, remove)
from telegram_bot.localization import localization
from telegram_bot.models import User
from youtube.models import ChannelUserItem


@log_errors
def inline_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    query.answer()

    u, _ = User.get_or_create_profile(
        query.message.chat_id, query.message.from_user)

    mode, query_data = query.data.split(f'{settings.SPLITTING_CHARACTER}')[
        0], query.data.split(f'{settings.SPLITTING_CHARACTER}')[1:]

    if mode == 'lang':
        u.language = query_data[0]
        u.save()

        query.edit_message_text(
            text=localization[query_data[0]]['lang_start_command'][1],
            parse_mode='HTML'
        )
    elif mode == 'start':
        u.language = query_data[0]
        u.save()

        keyboard = [
            [KeyboardButton(manage_command_text)],
            [KeyboardButton(language_command_text)],
            [KeyboardButton(help_command_text)],
            [KeyboardButton(upgrade_command_text)]
        ]

        reply_markup = ReplyKeyboardMarkup(keyboard)

        query.delete_message()
        context.bot.send_message(chat_id=update.effective_chat.id, text=localization[u.language]['help_command'][0],
                                 parse_mode='HTML',
                                 reply_markup=reply_markup)
    elif mode == 'add':
        if query_data[-1] == 'yes':
            query.edit_message_text(
                text=localization[u.language]['add_command'][1],
                parse_mode='HTML'
            )
            User.set_menu_field(
                u, f"name{settings.SPLITTING_CHARACTER}{query_data[0]}")
        else:
            query.delete_message()
            asyncio.run(add(query_data[-1], update, u))
    elif mode == 'manage':
        channel_id = query_data[-2]
        try:
            channel_name = [channel.channel_title for channel in ChannelUserItem.objects.filter(
                user=u) if channel.channel.channel_id == channel_id][0]
            remove(
                update, u, channel_name) if query_data[-1] == 'remove' else mute(update, u, channel_name)
        except:
            query.edit_message_text(
                text=localization[u.language]['remove_command'][3],
                parse_mode='HTML'
            )
    elif mode == 'pagination':
        page_num = int(query_data[-1])

        reply_markup = InlineKeyboardMarkup(
            get_manage_inline_keyboard(u, page_num))

        query.edit_message_text(
            text=localization[u.language]['remove_command'][0],
            parse_mode='HTML',
            reply_markup=reply_markup)
    elif mode == 'echo':
        channel_id = query_data[-2]
        if any(command in query_data for command in ['check', 'remove']):
            try:
                channel_name = [channel.channel_title for channel in ChannelUserItem.objects.filter(
                    user=u) if channel.channel.channel_id == channel_id][0]
                check(update, u, channel_name) if 'check' in query_data else remove(
                    update, u, channel_name)
            except Exception as e:
                query.edit_message_text(
                    text=localization[u.language]['echo'][4],
                    parse_mode='HTML'
                )
        elif any(command in query_data for command in ['yes', 'no']):
            query.delete_message() if 'yes' in query_data else query.edit_message_text(
                text=localization[u.language]['echo'][5], parse_mode='HTML')
            if 'yes' in query_data:
                keyboard = [
                    [
                        InlineKeyboardButton(
                            'Yes' if u.language == 'en' else 'Да', callback_data=f'add{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}yes'),
                        InlineKeyboardButton(
                            'No' if u.language == 'en' else 'Нет', callback_data=f'add{settings.SPLITTING_CHARACTER}{channel_id}')
                    ]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                User.set_menu_field(u)

                query.message.reply_text(
                    text=localization[u.language]['echo'][0],
                    parse_mode='HTML',
                    reply_markup=reply_markup)
    else:
        pass
