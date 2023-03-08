from bellify_bot.handlers.channels_adding_handler import add
from bellify_bot.localization import localization
from bellify_bot.models import ChannelUserItem, User
from django.conf import settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from twitch.utils import get_title_from_url, get_users_info
from utils.general_utils import get_channel_url_type
from utils.inline_utils import get_upgrade_inline_keyboard, log_errors
from youtube.utils import scrape_id_and_title_by_url


@log_errors
def echo_handler(update: Update, context: CallbackContext) -> None:
    u: User

    u, _ = User.get_or_create_profile(
        update.message.chat_id, update.message.from_user, False)
    user_text = update.message.text

    try:
        echo_data = u.menu.split(f'{settings.SPLITTING_CHARACTER}')
    except Exception as e:
        echo_data = ['']

    if all(echo_data):
        if 'name' in echo_data:
            if not get_channel_url_type(user_text):
                u.set_menu_field()
                channel_id, channel_type = echo_data[-3], echo_data[-2]
                add(channel_id, channel_type, update.message,
                    u, user_text.strip())
            else:
                update.message.reply_text(
                    text=localization[u.language]['echo'][7],
                    parse_mode='HTML',
                    disable_web_page_preview=True,
                    reply_markup=reply_markup)
    else:
        channel_type = get_channel_url_type(user_text)
        if channel_type:
            if 'YouTube' in channel_type:
                channel_id, channel_title = scrape_id_and_title_by_url(
                    user_text)
                if not (channel_id and channel_title):
                    update.message.reply_text(
                        text=localization[u.language]['echo'][5],
                        parse_mode='HTML',)
                    return
            elif 'Twitch' in channel_type:
                try:
                    channel_id, _, channel_title = get_users_info(
                        usernames=[get_title_from_url(user_text)])[0]
                except IndexError as e:
                    update.message.reply_text(
                        text=localization[u.language]['echo'][5],
                        parse_mode='HTML',)
                    return
            if ChannelUserItem.is_user_subscribed_to_channel(u, channel_id):
                keyboard = [
                    [
                        InlineKeyboardButton(
                            '🗑️', callback_data=f'link{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}remove'),
                        InlineKeyboardButton(
                            '❌', callback_data=f'link{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}cancel')
                    ]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                update.message.reply_text(
                    text=localization[u.language]['echo'][1],
                    parse_mode='HTML',
                    disable_web_page_preview=True,
                    reply_markup=reply_markup)
            elif 'B' in u.status and not 'YouTube' in channel_type:
                update.message.reply_text(
                    text=localization[u.language]['echo'][3],
                    parse_mode='HTML',
                    reply_markup=InlineKeyboardMarkup(
                        get_upgrade_inline_keyboard(u, 'premium'))
                )
            elif ChannelUserItem.get_count_by_user_and_channel(u, channel_type=channel_type) <= User.get_max_for_channel(u, channel_type=channel_type):
                keyboard = [
                    [
                        InlineKeyboardButton(
                            '✔️', callback_data=f'add{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}{channel_type}'),
                        InlineKeyboardButton(
                            '❌', callback_data=f'add{settings.SPLITTING_CHARACTER}{channel_id}{settings.SPLITTING_CHARACTER}{channel_type}{settings.SPLITTING_CHARACTER}no')
                    ]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                u.set_menu_field()

                if u.is_tutorial_finished:
                    update.message.reply_text(
                        text=f"{localization[u.language]['echo'][0][0]}<a href=\"{user_text}\">{channel_title}</a>{localization[u.language]['echo'][0][1]}",
                        parse_mode='HTML',
                        disable_web_page_preview=True,
                        reply_markup=reply_markup)
                else:
                    update.message.reply_text(
                        text=f"{localization[u.language]['help'][2][0]}<a href=\"{user_text}\">{channel_title}</a>{localization[u.language]['help'][2][1]}",
                        parse_mode='HTML',
                        disable_web_page_preview=True,
                        reply_markup=reply_markup)
            else:
                update.message.reply_text(
                    text=localization[u.language]['echo'][4][0 if u.is_tutorial_finished else 1],
                    parse_mode='HTML',
                    reply_markup=InlineKeyboardMarkup(get_upgrade_inline_keyboard(
                        u, mode='quota_echo', channel_type=channel_type.lower()))
                )
        else:
            pass
