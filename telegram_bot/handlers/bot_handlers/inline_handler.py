from django.conf import settings
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, Update)
from telegram.ext import CallbackContext
from telegram_bot.handlers.bot_handlers.utils import (
    _get_keyboard, add, get_manage_inline_keyboard, get_upgrade_inline_keyboard, log_errors, mute, remove,
    reply_invoice, upgrade, channels_type_name)
from telegram_bot.localization import localization
from telegram_bot.models import User
from twitch.models import ChannelUserItem


@log_errors
def inline_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    query.answer()

    u, _ = User.get_or_create_profile(
        query.message.chat_id, query.message.from_user)

    mode, query_data = query.data.split(f'{settings.SPLITTING_CHARACTER}')[
        0], query.data.split(f'{settings.SPLITTING_CHARACTER}')[1:]

    if mode in ['lang', 'start', 'tutorial']:
        if mode == 'tutorial':
            User.change_tutorial_state(u, False)
        if mode == 'lang' or u.is_tutorial_finished:
            u.language = query_data[0]
            u.save()

            reply_markup = ReplyKeyboardMarkup(_get_keyboard(u))

            query.delete_message()
            query.message.reply_text(
                text=localization[query_data[0]]['lang_start_command'][1],
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        else:
            query.message.reply_text(
                text=localization[u.language]['help'][1],
                parse_mode='HTML',
            )
            for channel_id in settings.SAMPLE_CHANNELS_IDS:
                if not ChannelUserItem.is_user_subscribed_to_channel(u, channel_id):
                    query.message.reply_text(
                        text=f'https://www.youtube.com/c/{channel_id}',
                        parse_mode='HTML',
                    )
                    break
    elif mode == 'add':
        if query_data[-1] == 'yes':
            query.edit_message_text(
                text=localization[u.language]['add'][0],
                parse_mode='HTML'
            )
            User.set_menu_field(
                u, f"name{settings.SPLITTING_CHARACTER}{query_data[0]}{settings.SPLITTING_CHARACTER}{query_data[1]}")
        else:
            channel_id, channel_type = query_data[-2], query_data[-1]
            query.delete_message()
            add(channel_id, channel_type, update.callback_query.message, u)
    elif mode == 'manage':
        channel_id = query_data[-2]
        channel = ChannelUserItem.get_user_channel_by_id(u, channel_id)
        remove(
            update, u, channel) if query_data[-1] == 'remove' else mute(update, u, channel)
    elif mode == 'upgrade':
        def _premium():
            reply_invoice(update, u, localization[u.language]['upgrade'][3][0], localization[u.language]
                          ['upgrade'][3][1], f'youtube{settings.SPLITTING_CHARACTER}premium', localization[u.language]['upgrade'][3][2], settings.PREMIUM_PRICE)

        def _channel_increase():
            query.message.reply_text(
                text=localization[u.language]['upgrade'][4],
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup(
                    get_upgrade_inline_keyboard(u, 'quota'))
            )

        def _quota():
            reply_invoice(update, u, f"{localization[u.language]['upgrade'][5][0][0]} {channels_type_name[query_data[-2]]} {localization[u.language]['upgrade'][5][0][1]}",
                          f"{localization[u.language]['upgrade'][5][1][0]} {channels_type_name[query_data[-2]]} {localization[u.language]['upgrade'][5][1][1]} (+{query_data[-1]}).",
                          f'{query_data[-2]}{settings.SPLITTING_CHARACTER}{query_data[-1]}', localization[u.language]['upgrade'][5][2], int(
                              query_data[-1]) * settings.INCREASE_PRICES[query_data[-2]],
                          'quota')

        query.delete_message()
        if 'back' in query_data:
            if query_data[-1] == 'upgrade':
                upgrade(query.message, u)
            elif query_data[-1] == 'quota':
                _channel_increase()
        elif query_data[-1] == 'premium':
            _premium()
        elif query_data[-1] in channels_type_name:
            _channel_increase()
        elif query_data[0] == 'quota':
            _quota()
    elif mode == 'pagination':
        page_num = int(query_data[-1])

        reply_markup = InlineKeyboardMarkup(
            get_manage_inline_keyboard(u, page_num))

        query.edit_message_text(
            text=localization[u.language]['manage'][0],
            parse_mode='HTML',
            reply_markup=reply_markup)
    elif mode == 'echo':
        channel_id, channel_type = query_data[-3], query_data[-2]
        if 'remove' in query_data:
            try:
                channel = ChannelUserItem.get_user_channel_by_id(u, channel_id)
                remove(update, u, channel)
            except Exception as e:
                query.edit_message_text(
                    text=localization[u.language]['echo'][2],
                    parse_mode='HTML'
                )
        elif 'cancel' in query_data:
            query.delete_message()
    else:
        pass
