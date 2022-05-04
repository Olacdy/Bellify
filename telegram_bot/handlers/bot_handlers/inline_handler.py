from django.conf import settings
from telegram import (InlineKeyboardButton,
                      InlineKeyboardMarkup, ReplyKeyboardMarkup, Update)
from telegram.ext import CallbackContext
from telegram_bot.handlers.bot_handlers.utils import (
    add_youtube_channel, get_manage_inline_keyboard, log_errors, mute, remove, _get_keyboard)
from telegram_bot.localization import localization
from telegram_bot.models import User
from youtube.models import YoutubeChannelUserItem


@log_errors
def inline_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    query.answer()

    u, _ = User.get_or_create_profile(
        query.message.chat_id, query.message.from_user)

    mode, query_data = query.data.split(f'{settings.SPLITTING_CHARACTER}')[
        0], query.data.split(f'{settings.SPLITTING_CHARACTER}')[1:]

    if mode == 'lang' or mode == 'start':
        u.language = query_data[0]
        u.save()

        reply_markup = ReplyKeyboardMarkup(_get_keyboard(u))

        query.delete_message()
        context.bot.send_message(chat_id=update.effective_chat.id, text=localization[query_data[0]]['lang_start_command'][1] if mode == 'lang' else localization[query_data[0]]['help'][0],
                                 parse_mode='HTML',
                                 reply_markup=reply_markup)
    elif mode == 'add':
        if query_data[-1] == 'yes':
            query.edit_message_text(
                text=localization[u.language]['add'][0],
                parse_mode='HTML'
            )
            User.set_menu_field(
                u, f"name{settings.SPLITTING_CHARACTER}{query_data[0]}")
        else:
            query.delete_message()
            add_youtube_channel(
                query_data[-1], update.callback_query.message, u)
    elif mode == 'manage':
        channel_id = query_data[-2]
        channel_name = [channel.channel_title for channel in YoutubeChannelUserItem.objects.filter(
            user=u) if channel.channel.channel_id == channel_id][0]
        remove(
            update, u, channel_name) if query_data[-1] == 'remove' else mute(update, u, channel_name)
    elif mode == 'pagination':
        page_num = int(query_data[-1])

        reply_markup = InlineKeyboardMarkup(
            get_manage_inline_keyboard(u, page_num))

        query.edit_message_text(
            text=localization[u.language]['manage'][0],
            parse_mode='HTML',
            reply_markup=reply_markup)
    elif mode == 'echo':
        channel_id = query_data[-2]
        if 'remove' in query_data:
            try:
                channel_name = [channel.channel_title for channel in YoutubeChannelUserItem.objects.filter(
                    user=u) if channel.channel.channel_id == channel_id][0]
                remove(update, u, channel_name)
            except Exception as e:
                query.edit_message_text(
                    text=localization[u.language]['echo'][3],
                    parse_mode='HTML'
                )
        elif 'cancel' in query_data:
            query.delete_message()
        elif any(command in query_data for command in ['yes', 'no']):
            query.delete_message()
            if 'yes' in query_data:
                keyboard = [
                    [
                        InlineKeyboardButton(
                            '✔️', callback_data=f'add{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}yes'),
                        InlineKeyboardButton(
                            '❌', callback_data=f'add{settings.SPLITTING_CHARACTER}{channel_id}')
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
