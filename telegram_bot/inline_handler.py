from celery import local
from telegram import Update
from django.conf import settings
from telegram.ext import CallbackContext
from youtube.models import ChannelUserItem
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .utils import get_or_create_profile, log_errors, set_menu_field, add, check, remove
from .localization import localization


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

            keyboard = []
            pagination_button_set = []

            channels = [ChannelUserItem.objects.filter(
                user=p)[i:i + settings.PAGINATION_SIZE] for i in range(0, len(ChannelUserItem.objects.filter(user=p)), settings.PAGINATION_SIZE)]

            for channel in channels[page_num]:
                keyboard.append([
                    InlineKeyboardButton(
                        f'{channel.channel_title}', callback_data=f'check‽{channel.channel.channel_id}')
                ])

            pagination_button_set.append(InlineKeyboardButton(
                '❮', callback_data=f'check‽pagination‽{page_num - 1}')) if page_num - 1 >= 0 else None
            pagination_button_set.append(InlineKeyboardButton(
                '❯', callback_data=f'check‽pagination‽{page_num + 1}')) if page_num + 1 < len(channels) else None
            keyboard.append(
                pagination_button_set) if pagination_button_set else None
            reply_markup = InlineKeyboardMarkup(keyboard)

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

            keyboard = []
            pagination_button_set = []

            channels = [ChannelUserItem.objects.filter(
                user=p)[i:i + settings.PAGINATION_SIZE] for i in range(0, len(ChannelUserItem.objects.filter(user=p)), settings.PAGINATION_SIZE)]

            for channel in channels[page_num]:
                keyboard.append([
                    InlineKeyboardButton(
                        f'{channel.channel_title}', callback_data=f'remove‽{channel.channel.channel_id}')
                ])

            pagination_button_set.append(InlineKeyboardButton(
                '❮', callback_data=f'remove‽pagination‽{page_num - 1}')) if page_num - 1 >= 0 else None
            pagination_button_set.append(InlineKeyboardButton(
                '❯', callback_data=f'remove‽pagination‽{page_num + 1}')) if page_num + 1 < len(channels) else None
            keyboard.append(
                pagination_button_set) if pagination_button_set else None
            reply_markup = InlineKeyboardMarkup(keyboard)

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

            keyboard = []
            pagination_button_set = []

            channels = [ChannelUserItem.objects.filter(
                user=p)[i:i + settings.PAGINATION_SIZE] for i in range(0, len(ChannelUserItem.objects.filter(user=p)), settings.PAGINATION_SIZE)]

            for channel in channels[page_num]:
                keyboard.append([
                    InlineKeyboardButton(
                        f'{channel.channel_title}', url=channel.channel.channel_url)
                ])

            pagination_button_set.append(InlineKeyboardButton(
                '❮', callback_data=f'list‽pagination‽{page_num - 1}')) if page_num - 1 >= 0 else None
            pagination_button_set.append(InlineKeyboardButton(
                '❯', callback_data=f'list‽pagination‽{page_num + 1}')) if page_num + 1 < len(channels) else None
            keyboard.append(
                pagination_button_set) if pagination_button_set else None
            reply_markup = InlineKeyboardMarkup(keyboard)

            query.edit_message_text(
                text=localization[p.language]['list_command'][0],
                parse_mode='HTML',
                reply_markup=reply_markup)
    else:
        pass
