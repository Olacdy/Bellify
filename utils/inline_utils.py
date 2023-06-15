from typing import Optional

from bellify_bot.localization import localization
from bellify_bot.models import ChannelUserItem, User
from telegram import InlineKeyboardMarkup, Message, Update

from utils.general_utils import get_manage_message
from utils.keyboards import (get_manage_inline_keyboard,
                             get_upgrade_inline_keyboard, log_errors)


# Removes given channel user item
@log_errors
def remove(update: Update, u: User, channel: ChannelUserItem, page_num: Optional[int] = 0) -> None:
    channel.delete() if u.is_tutorial_finished and channel else None
    manage(update, u, mode='remove', page_num=page_num)


# Mutes given channel user item
@log_errors
def mute(update: Update, u: User, channel: ChannelUserItem, page_num: Optional[int] = 0) -> None:
    channel.mute_channel() if channel else None
    manage(update, u, mode='mute', page_num=page_num)


# Returns Manage replies according to call situation
@log_errors
def manage(update: Update, u: User, mode: Optional[str] = 'echo', page_num: Optional[int] = 0) -> None:
    keyboard = get_manage_inline_keyboard(u, page_num=page_num)

    if keyboard:
        reply_markup = InlineKeyboardMarkup(keyboard)

        if 'echo' in mode:
            update.message.reply_text(
                text=get_manage_message(u, mode='echo'),
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            update.callback_query.edit_message_text(
                text=get_manage_message(u),
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            u.set_tutorial_state(True) if not u.is_tutorial_finished else None
    else:
        if 'echo' in mode:
            update.message.reply_text(
                text=localization[u.language]['manage'][1],
                parse_mode='HTML'
            )
        else:
            update.callback_query.edit_message_text(
                text=localization[u.language]['manage'][2],
                parse_mode='HTML'
            )


# First reply on Upgrade command
@log_errors
def upgrade(message: Message, u: User):
    message.reply_text(
        text=localization[u.language]['upgrade'][0],
        reply_markup=InlineKeyboardMarkup(get_upgrade_inline_keyboard(u)),
        parse_mode='HTML'
    )
