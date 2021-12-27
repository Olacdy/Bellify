from telegram import Update
from django.conf import settings
from telegram.ext import CallbackContext
from youtube.models import ChannelUserItem
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .utils import get_or_create_profile, log_errors, set_menu_field, add, check, remove


@log_errors
def inline_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    query.answer()

    p, _ = get_or_create_profile(
        query.message.chat_id, query.message.from_user)

    mode = query.data.split(', ')[0]

    if mode == 'lang':
        lang_for_lang = {
            'en': 'Thanks, You\'ll continue work on English.',
            'ru': 'Спасибо, теперь работа будет продолжена на русском.'
        }

        p.language = query.data.split(', ')[1]
        p.save()

        query.edit_message_text(
            text=lang_for_lang[query.data.split(', ')[1]],
            parse_mode='HTML'
        )

    elif mode == 'add':
        lang_for_add = {
            'en': 'Send Your custom channel name.',
            'ru': 'Можете прислать имя, под которым хотите сохранить канал.'
        }

        if query.data.split(', ')[-1] == 'yes':
            query.edit_message_text(
                text=lang_for_add[p.language],
                parse_mode='HTML'
            )
            set_menu_field(p, f"name_{query.data.split(', ')[1]}")
        else:
            query.delete_message()
            add(query.data.split(', ')[-1], update, p)
    elif mode == 'check':
        lang_for_check = {
            'en':
                [
                    'No channel with such name.',
                    'Select a channel that You would like to check.'
                ],
            'ru':
                [
                    'Канала с таким именем не существует.',
                    'Выберите канал, который вы хотите проверить.'
                ]
        }

        if 'pagination' in query.data.split(', '):
            page_num = int(query.data.split(
                ', ')[-1])

            keyboard = []
            pagination_button_set = []

            channels = [ChannelUserItem.objects.filter(
                user=p)[i:i + settings.PAGINATION_SIZE] for i in range(0, len(ChannelUserItem.objects.filter(user=p)), settings.PAGINATION_SIZE)]

            for channel in channels[page_num]:
                keyboard.append([
                    InlineKeyboardButton(
                        f'{channel.channel_title}', callback_data=f'check, {channel.channel.channel_id}')
                ])

            pagination_button_set.append(InlineKeyboardButton(
                'Previous' if p.language == 'en' else 'Назад', callback_data=f'check, pagination, {page_num - 1}')) if page_num - 1 >= 0 else None
            pagination_button_set.append(InlineKeyboardButton(
                'Next' if p.language == 'en' else 'Вперед', callback_data=f'check, pagination, {page_num + 1}')) if page_num + 1 < len(channels) else None
            keyboard.append(
                pagination_button_set) if pagination_button_set else None
            reply_markup = InlineKeyboardMarkup(keyboard)

            query.edit_message_text(
                text=lang_for_check[p.language][1],
                parse_mode='HTML',
                reply_markup=reply_markup)
        else:
            channel_id = query.data.split(', ')[-1]
            try:
                channel_name = [channel.channel_title for channel in ChannelUserItem.objects.filter(
                    user=p) if channel.channel.channel_id == channel_id][0]
                check(update, p, channel_name)
            except:
                query.edit_message_text(
                    text=lang_for_check[p.language][0],
                    parse_mode='HTML'
                )
    elif mode == 'remove':
        lang_for_remove = {
            'en':
                [
                    'No channel with such name.',
                    'Select a channel that You would like to remove.'
                ],
            'ru':
                [
                    'Канала с таким именем не существует.',
                    'Выберите канал, который вы хотите удалить.'
                ]
        }

        if 'pagination' in query.data.split(', '):
            page_num = int(query.data.split(
                ', ')[-1])

            keyboard = []
            pagination_button_set = []

            channels = [ChannelUserItem.objects.filter(
                user=p)[i:i + settings.PAGINATION_SIZE] for i in range(0, len(ChannelUserItem.objects.filter(user=p)), settings.PAGINATION_SIZE)]

            for channel in channels[page_num]:
                keyboard.append([
                    InlineKeyboardButton(
                        f'{channel.channel_title}', callback_data=f'remove, {channel.channel.channel_id}')
                ])

            pagination_button_set.append(InlineKeyboardButton(
                'Previous' if p.language == 'en' else 'Назад', callback_data=f'remove, pagination, {page_num - 1}')) if page_num - 1 >= 0 else None
            pagination_button_set.append(InlineKeyboardButton(
                'Next' if p.language == 'en' else 'Вперед', callback_data=f'remove, pagination, {page_num + 1}')) if page_num + 1 < len(channels) else None
            keyboard.append(
                pagination_button_set) if pagination_button_set else None
            reply_markup = InlineKeyboardMarkup(keyboard)

            query.edit_message_text(
                text=lang_for_remove[p.language][1],
                parse_mode='HTML',
                reply_markup=reply_markup)
        else:
            channel_id = query.data.split(', ')[-1]
            try:
                channel_name = [channel.channel_title for channel in ChannelUserItem.objects.filter(
                    user=p) if channel.channel.channel_id == channel_id][0]
                remove(update, p, channel_name)
            except:
                query.edit_message_text(
                    text=lang_for_remove[p.language][0],
                    parse_mode='HTML'
                )
    elif mode == 'list':
        lang_for_list = {
            'en':
                [
                    'List of Your added channels.'
                ],
            'ru':
                [
                    'Список добавленных вами каналов',
                ]
        }
        if 'pagination' in query.data.split(', '):
            page_num = int(query.data.split(
                ', ')[-1])

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
                'Previous' if p.language == 'en' else 'Назад', callback_data=f'list, pagination, {page_num - 1}')) if page_num - 1 >= 0 else None
            pagination_button_set.append(InlineKeyboardButton(
                'Next' if p.language == 'en' else 'Вперед', callback_data=f'list, pagination, {page_num + 1}')) if page_num + 1 < len(channels) else None
            keyboard.append(
                pagination_button_set) if pagination_button_set else None
            reply_markup = InlineKeyboardMarkup(keyboard)

            query.edit_message_text(
                text=lang_for_list[p.language][0],
                parse_mode='HTML',
                reply_markup=reply_markup)
    else:
        pass
