from typing import List, Optional

from bellify_bot.localization import localization
from bellify_bot.models import ChannelUserItem, User
from django.conf import settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from utils.general_utils import log_errors


# Returns Language inline keyboard
@log_errors
def get_language_inline_keyboard(user_lang: Optional[str] = 'en', command: Optional[str] = 'language') -> List[List[InlineKeyboardButton]]:

    if 'language' in command or 'start' in command:
        keyboard = [
            [
                InlineKeyboardButton(
                    '🇬🇧English', callback_data=f'{command}{settings.SPLITTING_CHARACTER}en')
            ],
            [
                InlineKeyboardButton(
                    '🇷🇺Русский', callback_data=f'{command}{settings.SPLITTING_CHARACTER}ru'),
                InlineKeyboardButton(
                    '🇺🇦Українська', callback_data=f'{command}{settings.SPLITTING_CHARACTER}ua'),
            ]
        ]
    elif 'settings' in command:
        keyboard = [
            InlineKeyboardButton(
                f'{"🔘" if user_lang == "en" else "⚪️"} 🇬🇧', callback_data=f'{command}{settings.SPLITTING_CHARACTER}language{settings.SPLITTING_CHARACTER}en'),
            InlineKeyboardButton(
                f'{"🔘" if user_lang == "ru" else "⚪️"} 🇷🇺', callback_data=f'{command}{settings.SPLITTING_CHARACTER}language{settings.SPLITTING_CHARACTER}ru'),
            InlineKeyboardButton(
                f'{"🔘" if user_lang == "ua" else "⚪️"} 🇺🇦', callback_data=f'{command}{settings.SPLITTING_CHARACTER}language{settings.SPLITTING_CHARACTER}ua')
        ]

    return keyboard


# Returns settings keyboard
@log_errors
def get_settings_inline_keyboard(u: User):
    keyboard = [
        [
            InlineKeyboardButton(
                f'{"❌" if u.is_message_icons_disabled else "✔️"} {localization[u.language]["settings"][1][0]}', callback_data=f'settings{settings.SPLITTING_CHARACTER}message{settings.SPLITTING_CHARACTER}icons')

        ],
        [
            InlineKeyboardButton(
                f'{"❌" if u.is_manage_icons_disabled else "✔️"} {localization[u.language]["settings"][1][1]}', callback_data=f'settings{settings.SPLITTING_CHARACTER}manage{settings.SPLITTING_CHARACTER}icons')
        ],
        [
            InlineKeyboardButton(
                f'{"❌" if u.is_twitch_thumbnail_disabled else "✔️"} {localization[u.language]["settings"][1][2]}', callback_data=f'settings{settings.SPLITTING_CHARACTER}twitch{settings.SPLITTING_CHARACTER}thumbnail')
        ],
        get_language_inline_keyboard(user_lang=u.language, command='settings')
    ]

    return keyboard


# Returns Upgrade inline keyboard
@log_errors
def get_upgrade_inline_keyboard(u: User, mode: Optional[str] = 'upgrade', channel_type: Optional[str] = 'youtube') -> List[List[InlineKeyboardButton]]:
    keyboard = [[]]

    if 'upgrade' in mode:
        keyboard.append(
            [
                InlineKeyboardButton(
                    localization[u.language]['upgrade'][1], callback_data=f'upgrade{settings.SPLITTING_CHARACTER}premium')
            ]
        ) if u.status == 'B' else None

        keyboard.append(
            [
                InlineKeyboardButton(
                    f"{localization[u.language]['upgrade'][2][0]} {settings.CHANNELS_INFO['youtube']['name']} {localization[u.language]['upgrade'][2][1]}", callback_data=f'upgrade{settings.SPLITTING_CHARACTER}youtube')
            ]
        )

        keyboard.append(
            [
                InlineKeyboardButton(
                    f"{localization[u.language]['upgrade'][2][0]} {settings.CHANNELS_INFO['twitch']['name']} {localization[u.language]['upgrade'][2][1]}", callback_data=f'upgrade{settings.SPLITTING_CHARACTER}twitch')
            ]
        ) if u.status == 'P' else None
    elif 'quota' in mode:
        for amount in settings.CHANNELS_INFO[channel_type]['increase_amount']:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"{settings.CHANNELS_INFO[channel_type]['icon']} {amount}", callback_data=f'upgrade{settings.SPLITTING_CHARACTER}{mode}{settings.SPLITTING_CHARACTER}{channel_type}{settings.SPLITTING_CHARACTER}{amount}')
                ]
            )
        keyboard.append(
            [
                InlineKeyboardButton(
                    localization[u.language]['upgrade'][6], callback_data=f"upgrade{settings.SPLITTING_CHARACTER}back{settings.SPLITTING_CHARACTER}upgrade")
            ]
        ) if not 'echo' in mode else None
    elif 'premium' in mode:
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
                    channel.manage_title_and_type, url=channel.channel.channel_url),
                InlineKeyboardButton(
                    f'🔕' if channel.is_muted else f'🔔', callback_data=f'manage{settings.SPLITTING_CHARACTER}{channel.channel.channel_id}{settings.SPLITTING_CHARACTER}{page_num}{settings.SPLITTING_CHARACTER}mute'),
                InlineKeyboardButton(
                    f'❌', callback_data=f'manage{settings.SPLITTING_CHARACTER}{channel.channel.channel_id}{settings.SPLITTING_CHARACTER}{page_num}{settings.SPLITTING_CHARACTER}remove')
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
def get_notification_reply_markup(content_title: str, url: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=content_title, url=url)]
    ])
