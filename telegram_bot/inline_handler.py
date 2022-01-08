from telegram import InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from youtube.models import ChannelUserItem

from .localization import localization
from .utils import (add, check, get_or_create_profile, log_errors, remove,
                    set_menu_field, get_inline_keyboard)


@log_errors
def inline_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    query.answer()

    p, _ = get_or_create_profile(
        query.message.chat_id, query.message.from_user)

    mode = query.data.split('‽')[0]

    if mode == 'lang':
        p.language = query.data.split('‽')[1]
        p.save()

        query.edit_message_text(
            text=localization[query.data.split(
                '‽')[1]]['lang_start_command'][1],
            parse_mode='HTML'
        )

    elif mode == 'add':
        if query.data.split('‽')[-1] == 'yes':
            query.edit_message_text(
                text=localization[p.language]['add_command'][1],
                parse_mode='HTML'
            )
            set_menu_field(p, f"name‽{query.data.split('‽')[1]}")
        else:
            query.delete_message()
            add(query.data.split('‽')[-1], update, p)
    elif mode == 'check':
        if 'pagination' in query.data.split('‽'):
            page_num = int(query.data.split(
                '‽')[-1])

            reply_markup = InlineKeyboardMarkup(
                get_inline_keyboard(p, 'check', page_num))

            query.edit_message_text(
                text=localization[p.language]['check_command'][0],
                parse_mode='HTML',
                reply_markup=reply_markup)
        else:
            channel_id = query.data.split('‽')[-1]
            try:
                channel_name = [channel.channel_title for channel in ChannelUserItem.objects.filter(
                    user=p) if channel.channel.channel_id == channel_id][0]
                check(update, p, channel_name)
            except:
                query.edit_message_text(
                    text=localization[p.language]['check_command'][2],
                    parse_mode='HTML'
                )
    elif mode == 'remove':
        if 'pagination' in query.data.split('‽'):
            page_num = int(query.data.split(
                '‽')[-1])

            reply_markup = InlineKeyboardMarkup(
                get_inline_keyboard(p, 'remove', page_num))

            query.edit_message_text(
                text=localization[p.language]['remove_command'][0],
                parse_mode='HTML',
                reply_markup=reply_markup)
        else:
            channel_id = query.data.split('‽')[-1]
            try:
                channel_name = [channel.channel_title for channel in ChannelUserItem.objects.filter(
                    user=p) if channel.channel.channel_id == channel_id][0]
                remove(update, p, channel_name)
            except:
                query.edit_message_text(
                    text=localization[p.language]['remove_command'][3],
                    parse_mode='HTML'
                )
    elif mode == 'list':
        if 'pagination' in query.data.split('‽'):
            page_num = int(query.data.split(
                '‽')[-1])

            reply_markup = InlineKeyboardMarkup(
                get_inline_keyboard(p, 'list', page_num, 'url'))

            query.edit_message_text(
                text=localization[p.language]['list_command'][0],
                parse_mode='HTML',
                reply_markup=reply_markup)
    else:
        pass
