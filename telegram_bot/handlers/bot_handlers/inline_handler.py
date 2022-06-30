from django.conf import settings
from telegram import CallbackQuery, InlineKeyboardMarkup, Update, error
from telegram.ext import CallbackContext
from telegram_bot.handlers.bot_handlers.utils import (
    add, get_manage_inline_keyboard, get_upgrade_inline_keyboard, log_errors,
    mute, remove, reply_invoice, upgrade)
from telegram_bot.localization import localization
from telegram_bot.models import User
from twitch.models import ChannelUserItem

from utils.general_utils import channels_type_name


@log_errors
def get_query_data_and_user(query: CallbackQuery):
    query.answer()

    u, _ = User.get_or_create_profile(
        query.message.chat_id, query.message.from_user)

    return query.data.split(f'{settings.SPLITTING_CHARACTER}')[1:], u


@log_errors
def inline_language_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query_data, u = get_query_data_and_user(query)

    User.set_language(u, query_data[0])

    query.delete_message()
    query.message.reply_text(
        text=localization[query_data[0]]['language_command'][1],
        parse_mode='HTML',
    )


@log_errors
def inline_start_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query_data, u = get_query_data_and_user(query)

    User.set_tutorial_state(u, False)
    User.set_language(u, query_data[0])

    query.delete_message()
    query.message.reply_text(
        text=localization[u.language if u.language else query_data[0]]['help'][1],
        parse_mode='HTML',
    )
    for channel_id in settings.SAMPLE_CHANNELS_IDS:
        if not ChannelUserItem.is_user_subscribed_to_channel(u, channel_id):
            query.message.reply_text(
                text=f'https://www.youtube.com/channel/{channel_id}',
                parse_mode='HTML',
            )
            break


@log_errors
def inline_tutorial_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    _, u = get_query_data_and_user(query)

    User.set_tutorial_state(u, False)

    query.delete_message()
    query.message.reply_text(
        text=localization[u.language]['help'][1],
        parse_mode='HTML',
    )
    for channel_id in settings.SAMPLE_CHANNELS_IDS:
        if not ChannelUserItem.is_user_subscribed_to_channel(u, channel_id):
            query.message.reply_text(
                text=f'https://www.youtube.com/channel/{channel_id}',
                parse_mode='HTML',
            )
            break


@log_errors
def inline_add_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query_data, u = get_query_data_and_user(query)

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


@log_errors
def inline_link_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query_data, u = get_query_data_and_user(query)

    channel_id = query_data[-2]
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


@log_errors
def inline_manage_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query_data, u = get_query_data_and_user(query)

    channel_id = query_data[-2]
    channel = ChannelUserItem.get_user_channel_by_id(u, channel_id)
    if query_data[-1] == 'mute':
        mute(update, u, channel)
    elif query_data[-1] == 'remove' and u.is_tutorial_finished:
        remove(
            update, u, channel)
    else:
        try:
            update.callback_query.edit_message_text(
                text=localization[u.language]["help"][6],
                reply_markup=InlineKeyboardMarkup(
                    get_manage_inline_keyboard(u)),
                parse_mode='HTML'
            )
        except error.BadRequest:
            pass


@log_errors
def inline_upgrade_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query_data, u = get_query_data_and_user(query)

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


@log_errors
def inline_pagination_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query_data, u = get_query_data_and_user(query)

    page_num = int(query_data[-1])

    reply_markup = InlineKeyboardMarkup(
        get_manage_inline_keyboard(u, page_num))

    query.edit_message_text(
        text=localization[u.language]['manage'][0],
        parse_mode='HTML',
        reply_markup=reply_markup)
