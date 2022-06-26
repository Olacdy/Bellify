from typing import List, Optional

from django.conf import settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from telegram_bot.localization import localization
from telegram_bot.models import ChannelUserItem, User

from utils.general_utils import channels_type_name, get_html_link, log_errors


# Returns Language inline keyboard
@log_errors
def get_language_inline_keyboard(command: Optional[str] = 'language') -> List[List[InlineKeyboardButton]]:
    keyboard = [
        [
            InlineKeyboardButton(
                '🇬🇧English', callback_data=f'{command}{settings.SPLITTING_CHARACTER}en'),
            InlineKeyboardButton(
                '🇷🇺Русский', callback_data=f'{command}{settings.SPLITTING_CHARACTER}ru')
        ]
    ]

    return keyboard


# Returns Upgrade inline keyboard
@log_errors
def get_upgrade_inline_keyboard(u: User, mode: Optional[str] = 'upgrade', channel_type: Optional[str] = 'youtube') -> List[List[InlineKeyboardButton]]:
    keyboard = [[]]

    if mode == 'upgrade':
        keyboard.append(
            [
                InlineKeyboardButton(
                    localization[u.language]['upgrade'][1], callback_data=f'upgrade{settings.SPLITTING_CHARACTER}premium')
            ]
        ) if u.status == 'B' else None

        keyboard.append(
            [
                InlineKeyboardButton(
                    f"{localization[u.language]['upgrade'][2][0]} {channels_type_name['youtube']} {localization[u.language]['upgrade'][2][1]}", callback_data=f'upgrade{settings.SPLITTING_CHARACTER}youtube')
            ]
        )

        keyboard.append(
            [
                InlineKeyboardButton(
                    f"{localization[u.language]['upgrade'][2][0]} {channels_type_name['twitch']} {localization[u.language]['upgrade'][2][1]}", callback_data=f'upgrade{settings.SPLITTING_CHARACTER}twitch')
            ]
        ) if u.status == 'P' else None
    elif mode == 'quota':
        for amount in settings.INCREASE_CHANNELS_AMOUNT:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"▶️ {amount}", callback_data=f'upgrade{settings.SPLITTING_CHARACTER}quota{settings.SPLITTING_CHARACTER}{channel_type}{settings.SPLITTING_CHARACTER}{amount}')
                ]
            )
        keyboard.append(
            [
                InlineKeyboardButton(
                    localization[u.language]['upgrade'][6], callback_data=f"upgrade{settings.SPLITTING_CHARACTER}back{settings.SPLITTING_CHARACTER}upgrade")
            ]
        )
    elif mode == 'premium':
        keyboard.append(
            [
                InlineKeyboardButton(
                    localization[u.language]['upgrade'][1], callback_data=f'upgrade{settings.SPLITTING_CHARACTER}premium')
            ]
        )

    return keyboard


# Returns Manage inline keyboard
@log_errors
def get_manage_inline_keyboard(u: User, page_num: Optional[int] = 0) -> List:
    keyboard = []
    pagination_button_set = []

    all_channels = ChannelUserItem.objects.filter(user=u).all()

    channels = [all_channels[i:i + settings.PAGINATION_SIZE]
                for i in range(0, len(all_channels), settings.PAGINATION_SIZE)]

    if channels:
        for channel in channels[page_num]:
            keyboard.append([
                InlineKeyboardButton(
                    f'{channel.channel_title}', url=channel.channel.channel_url),
                InlineKeyboardButton(
                    f'🔕' if channel.is_muted else f'🔔', callback_data=f'manage{settings.SPLITTING_CHARACTER}{channel.channel.channel_id}{settings.SPLITTING_CHARACTER}mute'),
                InlineKeyboardButton(
                    f'❌', callback_data=f'manage{settings.SPLITTING_CHARACTER}{channel.channel.channel_id}{settings.SPLITTING_CHARACTER}remove')
            ])

        pagination_button_set.append(InlineKeyboardButton(
            '❮', callback_data=f'pagination{settings.SPLITTING_CHARACTER}{page_num - 1}')) if page_num - 1 >= 0 else None
        pagination_button_set.append(InlineKeyboardButton(
            '❯', callback_data=f'pagination{settings.SPLITTING_CHARACTER}{page_num + 1}')) if page_num + 1 < len(channels) else None
        keyboard.append(
            pagination_button_set) if pagination_button_set else None

    return keyboard


# Returns Inline Keyboard with given title and url
@log_errors
def _get_notification_reply_markup(title: str, url: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text=title, url=url)]
    ])


# Returns keyboard with all basic commands
@log_errors
def _get_keyboard(language):
    keyboard = [
        [KeyboardButton(localization[language]['commands']
                        ['manage_command_text'])],
        [KeyboardButton(localization[language]['commands']
                        ['language_command_text'])],
        [KeyboardButton(localization[language]
                        ['commands']['help_command_text'])],
        [KeyboardButton(localization[language]['commands']
                        ['upgrade_command_text'])]
    ]

    return keyboard