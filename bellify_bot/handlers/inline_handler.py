from typing import List, Optional, Union

from bellify_bot.handlers.channels_adding_handler import add
from utils.inline_utils import (get_manage_inline_keyboard,
                                get_upgrade_inline_keyboard,
                                log_errors, mute, remove, upgrade)
from bellify_bot.localization import localization
from bellify_bot.models import User
from django.conf import settings
from telegram import CallbackQuery, InlineKeyboardMarkup, Update, error
from telegram.ext import CallbackContext
from twitch.models import ChannelUserItem

from utils.general_utils import (get_manage_message, reply_invoice,
                                 tutorial_reply)
from utils.keyboards import get_settings_inline_keyboard


@log_errors
def get_query_data_and_user(query: CallbackQuery) -> Union[List[str], User]:
    u: User

    query.answer()

    u, _ = User.get_or_create_profile(
        query.message.chat_id, query.message.from_user)

    return query.data.split(f'{settings.SPLITTING_CHARACTER}')[1:], u


@log_errors
def inline_language_handler(update: Update, context: CallbackContext) -> None:
    u: User

    query = update.callback_query
    query_data, u = get_query_data_and_user(query)

    u.set_language(query_data[-1])

    query.edit_message_text(
        text=localization[query_data[-1]]['language_command'][1],
        parse_mode='HTML',
    )


@log_errors
def inline_start_handler(update: Update, context: CallbackContext) -> None:
    u: User

    query = update.callback_query
    query_data, u = get_query_data_and_user(query)

    u.set_tutorial_state(False)
    u.set_language(query_data[-1])

    tutorial_reply(query, u.language if u.language else query_data[-1], u)


@log_errors
def inline_tutorial_handler(update: Update, context: CallbackContext) -> None:
    u: User

    query = update.callback_query
    _, u = get_query_data_and_user(query)

    u.set_tutorial_state(False)

    tutorial_reply(query, u.language, u)


@log_errors
def inline_add_handler(update: Update, context: CallbackContext) -> None:
    u: User

    query = update.callback_query
    query_data, u = get_query_data_and_user(query)

    if 'no' in query_data:
        query.edit_message_text(
            text=localization[u.language]['add'][0],
            parse_mode='HTML'
        )
        u.set_menu_field(
            f'name{settings.SPLITTING_CHARACTER}{settings.SPLITTING_CHARACTER.join(query_data[0:])}')
    else:
        channel_id, channel_type = query_data[0:]
        query.delete_message()
        add(channel_id, channel_type, query.message, u)


@log_errors
def inline_link_handler(update: Update, context: CallbackContext) -> None:
    u: User

    query = update.callback_query
    query_data, u = get_query_data_and_user(query)

    channel_id = query_data[-2]
    if 'remove' in query_data:
        try:
            channel = ChannelUserItem.get_channel_by_user_and_channel_id(
                u, channel_id)
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
    u: User

    query = update.callback_query
    query_data, u = get_query_data_and_user(query)

    mode, page_num, channel_id = query_data[-1], int(
        query_data[-2]), query_data[-3]
    channel = ChannelUserItem.get_channel_by_user_and_channel_id(u, channel_id)
    if 'mute' in mode:
        mute(update, u, channel, page_num=page_num)
    elif 'remove' in mode and u.is_tutorial_finished:
        remove(
            update, u, channel, page_num=page_num)


@log_errors
def inline_upgrade_handler(update: Update, context: CallbackContext) -> None:
    u: User

    query = update.callback_query
    query_data, u = get_query_data_and_user(query)

    def _premium() -> None:
        reply_invoice(update, u, localization[u.language]['upgrade'][3][0], localization[u.language]
                      ['upgrade'][3][1], f'youtube{settings.SPLITTING_CHARACTER}premium', localization[u.language]['upgrade'][3][2], settings.PREMIUM_PRICE)

    def _channel_increase(channel_type: str, mode: Optional[str] = 'quota') -> None:
        query.message.reply_text(
            text=f"{localization[u.language]['upgrade'][4][0]} {settings.CHANNELS_INFO[channel_type]['name']} {localization[u.language]['upgrade'][4][1]} {User.get_max_for_channel(u, settings.CHANNELS_INFO[channel_type]['name'])}.\n\n{localization[u.language]['upgrade'][4][2]}",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(
                get_upgrade_inline_keyboard(u, mode, channel_type))
        )

    def _quota(is_echo: bool) -> None:
        reply_invoice(update, u, f"{localization[u.language]['upgrade'][5][0][0]} {settings.CHANNELS_INFO[query_data[-2]]['name']} {localization[u.language]['upgrade'][5][0][1]}",
                      f"{localization[u.language]['upgrade'][5][1][0]} {settings.CHANNELS_INFO[query_data[-2]]['name']} {localization[u.language]['upgrade'][5][1][1]} (+{query_data[-1]}).",
                      f'{query_data[-2]}{settings.SPLITTING_CHARACTER}{query_data[-1]}', localization[u.language]['upgrade'][5][2], int(
                          query_data[-1]) * settings.CHANNELS_INFO[query_data[-2]]['increase_price'],
                      f'{f"echo{settings.SPLITTING_CHARACTER}" if is_echo else ""}{query_data[-2]}')

    try:
        query.delete_message()
    except error.BadRequest:
        pass

    if 'back' in query_data:
        if 'upgrade' in query_data:
            upgrade(query.message, u)
        elif query_data[-1] in settings.CHANNELS_INFO:
            _channel_increase(
                query_data[-1], 'quota_echo' if 'echo' in query_data else 'quota')
    elif 'premium' in query_data:
        _premium()
    elif query_data[-1] in settings.CHANNELS_INFO:
        _channel_increase(query_data[-1])
    elif 'quota' in query_data:
        _quota(False)
    elif 'quota_echo' in query_data:
        _quota(True)


@log_errors
def inline_settings_handler(update: Update, context: CallbackContext) -> None:
    u: User

    query = update.callback_query
    query_data, u = get_query_data_and_user(query)

    if 'icons' in query_data:
        if 'manage' in query_data:
            u.set_manage_icons_state()
        elif 'message' in query_data:
            u.set_message_icons_state()

        reply_markup = InlineKeyboardMarkup(
            get_settings_inline_keyboard(u))

        try:
            query.edit_message_reply_markup(
                reply_markup=reply_markup
            )
        except error.BadRequest:
            pass
    elif 'thumbnail' in query_data:
        u.set_twitch_thumbnail_state()

        reply_markup = InlineKeyboardMarkup(
            get_settings_inline_keyboard(u))

        try:
            query.edit_message_reply_markup(
                reply_markup=reply_markup
            )
        except error.BadRequest:
            pass
    elif 'language' in query_data:
        u.set_language(query_data[-1])

        reply_markup = InlineKeyboardMarkup(
            get_settings_inline_keyboard(u))

        try:
            query.edit_message_text(
                text=localization[query_data[-1]]['settings'][2],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        except error.BadRequest:
            pass


@ log_errors
def inline_pagination_handler(update: Update, context: CallbackContext) -> None:
    u: User

    query = update.callback_query
    query_data, u = get_query_data_and_user(query)

    page_num = int(query_data[-1])

    reply_markup = InlineKeyboardMarkup(
        get_manage_inline_keyboard(u, page_num))

    query.edit_message_text(
        text=get_manage_message(u, mode='pagination'),
        parse_mode='HTML',
        reply_markup=reply_markup)
