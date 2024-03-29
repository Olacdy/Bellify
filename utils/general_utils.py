import asyncio
from typing import Dict, List, Optional, Union

import aiohttp
import telegram
from asgiref import sync
from bellify_bot.localization import localization
from bellify_bot.models import ChannelUserItem, User
from django.conf import settings
from fake_headers import Headers
from telegram import (CallbackQuery, InlineKeyboardButton,
                      InlineKeyboardMarkup, LabeledPrice, MessageEntity,
                      Update)
from twitch.utils import is_twitch_url
from youtube.utils import is_youtube_url


def log_errors(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = f'Exception occured {e}'
            print(error_message)
            raise e

    return inner


# Checks if given string is url
@log_errors
def get_channel_url_type(string: str) -> Union[str, None]:
    if is_youtube_url(string):
        return 'YouTube'
    elif is_twitch_url(string):
        return 'Twitch'
    else:
        return None


# Returns html hyperlink
@log_errors
def get_html_link(url: str, title: Optional[str] = u'\u2060') -> str:
    return f'<a href=\"{url}\">{title}</a>'


# Returns bold html text
@log_errors
def get_html_bold(text: str) -> str:
    return f'<b>{text}</b>'


# Return message for manage command
@log_errors
def get_manage_message(u: User, mode: Optional[str] = None) -> str:
    blank_space = u'\u2060'

    dict_of_quota_info = {settings.CHANNELS_INFO[channel]['name']: User.get_max_for_channel(
        u, channel_type=settings.CHANNELS_INFO[channel]['name']) - ChannelUserItem.get_count_by_user_and_channel(u, channel_type=settings.CHANNELS_INFO[channel]['name']) + 1 for channel in settings.CHANNELS_INFO}

    remaining_quota_message = '\n'.join(
        filter(None, [f"{localization[u.language]['manage'][0][2]} {channel} {localization[u.language]['manage'][0][3]} {dict_of_quota_info[channel]}" if dict_of_quota_info[channel] > 0 else None for channel in dict_of_quota_info]))

    if mode in ['echo', 'pagination']:
        help_message = localization[u.language]['help'][4]
    else:
        help_message = localization[u.language]['help'][5]

    return f"{localization[u.language]['manage'][0][0 if u.status == 'P' else 1]}{blank_space}{' '*(118 - len(localization[u.language]['manage'][0][0 if u.status == 'P' else 1]))}{blank_space}\n{remaining_quota_message}" if u.is_tutorial_finished else help_message


# Makes a response on a tutorial start
def tutorial_reply(query: CallbackQuery, language: str, u: User) -> None:
    try:
        query.message.edit_text(
            text=f'{localization[language]["help"][1][0]}\n\n`{[f"https://www.youtube.com/channel/{channel_id}" for channel_id in settings.SAMPLE_CHANNELS_IDS if not ChannelUserItem.is_user_subscribed_to_channel(u, channel_id)][0]}`',
            parse_mode='MARKDOWN',
        )
    except IndexError:
        query.message.edit_text(
            text=f'{localization[language]["help"][1][1]}',
            parse_mode='MARKDOWN',
        )


# Reply on user invoice
@log_errors
def reply_invoice(update: Update, u: User, title: str, description: str, payload: str, buy_button_label: str, price: int, mode: Optional[str] = 'upgrade'):
    keyboard = [
        [
            InlineKeyboardButton(buy_button_label, pay=True)
        ],
        [
            InlineKeyboardButton(
                localization[u.language]['upgrade'][6], callback_data=f'upgrade{settings.SPLITTING_CHARACTER}back{settings.SPLITTING_CHARACTER}{mode}')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.callback_query.message.reply_invoice(
        title=title,
        description=description,
        payload=payload,
        provider_token=settings.PROVIDER_TOKEN,
        currency=settings.CURRENCY,
        prices=[LabeledPrice(description[:-1], (price - 1)
                             if not repr(price)[-1] == '5' else price)],
        reply_markup=reply_markup
    )


def send_messages(urls: List[str]) -> None:
    async def send_all(urls):
        async with aiohttp.ClientSession(cookies=settings.SESSION_CLIENT_COOKIES) as session:
            async def send(url):
                return await session.get(url, headers=Headers().generate())
            return await asyncio.gather(*[
                send(url) for url in urls
            ])
    sync.async_to_sync(send_all)(urls)


# Sends message to user
def _send_message(
    user_id: Union[str, int],
    text: str,
    parse_mode: Optional[str] = 'HTML',
    reply_markup: Optional[List[List[Dict]]] = None,
    reply_to_message_id: Optional[int] = None,
    disable_web_page_preview: Optional[bool] = None,
    disable_notification: Optional[bool] = None,
    entities: Optional[List[MessageEntity]] = None,
    tg_token: str = settings.TOKEN,
) -> bool:
    bot = telegram.Bot(tg_token)
    try:
        m = bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            entities=entities,
        )
    except telegram.error.Unauthorized:
        print(f'Can\'t send message to {user_id}. Reason: Bot was stopped.')
        User.objects.filter(user_id=user_id).update(is_blocked_bot=True)
        success = False
    else:
        success = True
        User.objects.filter(user_id=user_id).update(is_blocked_bot=False)
    return success


def _from_celery_markup_to_markup(celery_markup: Optional[List[List[Dict]]]) -> Optional[InlineKeyboardMarkup]:
    markup = None
    if celery_markup:
        markup = []
        for row_of_buttons in celery_markup:
            row = []
            for button in row_of_buttons:
                row.append(
                    InlineKeyboardButton(
                        text=button['text'],
                        callback_data=button.get('callback_data'),
                        url=button.get('url'),
                    )
                )
            markup.append(row)
        markup = InlineKeyboardMarkup(markup)
    return markup


def _from_celery_entities_to_entities(celery_entities: Optional[List[Dict]] = None) -> Optional[List[MessageEntity]]:
    entities = None
    if celery_entities:
        entities = [
            MessageEntity(
                type=entity['type'],
                offset=entity['offset'],
                length=entity['length'],
                url=entity.get('url'),
                language=entity.get('language'),
            )
            for entity in celery_entities
        ]
    return entities
