from telegram import InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from youtube.models import ChannelUserItem

from telegram_bot.localization import localization
from telegram_bot.handlers.bot_handlers.utils import (
    add, check, log_errors, remove, get_inline_keyboard)
from telegram_bot.models import User


@log_errors
def inline_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    query.answer()

    u, _ = User.get_or_create_profile(
        query.message.chat_id, query.message.from_user)

    mode = query.data.split('‽')[0]

    if mode == 'lang':
        u.language = query.data.split('‽')[1]
        u.save()

        query.edit_message_text(
            text=localization[query.data.split(
                '‽')[1]]['lang_start_command'][1],
            parse_mode='HTML'
        )

    elif mode == 'add':
        if query.data.split('‽')[-1] == 'yes':
            query.edit_message_text(
                text=localization[u.language]['add_command'][1],
                parse_mode='HTML'
            )
            User.set_menu_field(u, f"name‽{query.data.split('‽')[1]}")
        else:
            query.delete_message()
            add(query.data.split('‽')[-1], update, u)
    elif mode == 'check':
        if 'pagination' in query.data.split('‽'):
            page_num = int(query.data.split(
                '‽')[-1])

            reply_markup = InlineKeyboardMarkup(
                get_inline_keyboard(u, 'check', page_num))

            query.edit_message_text(
                text=localization[u.language]['check_command'][0],
                parse_mode='HTML',
                reply_markup=reply_markup)
        else:
            channel_id = query.data.split('‽')[-1]
            try:
                channel_name = [channel.channel_title for channel in ChannelUserItem.objects.filter(
                    user=u) if channel.channel.channel_id == channel_id][0]
                check(update, u, channel_name)
            except:
                query.edit_message_text(
                    text=localization[u.language]['check_command'][2],
                    parse_mode='HTML'
                )
    elif mode == 'remove':
        if 'pagination' in query.data.split('‽'):
            page_num = int(query.data.split(
                '‽')[-1])

            reply_markup = InlineKeyboardMarkup(
                get_inline_keyboard(u, 'remove', page_num))

            query.edit_message_text(
                text=localization[u.language]['remove_command'][0],
                parse_mode='HTML',
                reply_markup=reply_markup)
        else:
            channel_id = query.data.split('‽')[-1]
            try:
                channel_name = [channel.channel_title for channel in ChannelUserItem.objects.filter(
                    user=u) if channel.channel.channel_id == channel_id][0]
                remove(update, u, channel_name)
            except:
                query.edit_message_text(
                    text=localization[u.language]['remove_command'][3],
                    parse_mode='HTML'
                )
    elif mode == 'list':
        if 'pagination' in query.data.split('‽'):
            page_num = int(query.data.split(
                '‽')[-1])

            reply_markup = InlineKeyboardMarkup(
                get_inline_keyboard(u, 'list', page_num, 'url'))

            query.edit_message_text(
                text=localization[u.language]['list_command'][0],
                parse_mode='HTML',
                reply_markup=reply_markup)
    else:
        pass
