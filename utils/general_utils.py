from typing import Dict, List, Optional, Union

import telegram
from django.conf import settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity, CallbackQuery
from bellify_bot.models import User
from twitch.utils import is_twitch_channel_url
from youtube.utils import is_youtube_channel_url
from bellify_bot.localization import localization
from bellify_bot.models import ChannelUserItem


# Channgels in lowercase аccording to their name
channels_type_name = {
    'youtube': "Youtube",
    'twitch': "Twitch"
}


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
    if is_youtube_channel_url(string):
        return 'YouTube'
    elif is_twitch_channel_url(string):
        return 'Twitch'
    else:
        return None


# Returns html hyperlink
@log_errors
def get_html_link(url: str, title: str) -> str:
    return f'<a href=\"{url}\">{title}</a>'


# Makes a response on a tutorial start
def tutorial_reply(query: CallbackQuery, language: str, u: User) -> None:
    query.delete_message()
    query.message.reply_text(
        text=f'{localization[language]["help"][1]}\n\n`{[f"https://www.youtube.com/channel/{channel_id}" for channel_id in settings.SAMPLE_CHANNELS_IDS if not ChannelUserItem.is_user_subscribed_to_channel(u, channel_id)][0]}`',
        parse_mode='MARKDOWN',
    )


# Return Bot response message for Twitch channel adding
def get_twitch_channel_message(u: User, channel_url: str, channel_name: str, live_title: str, game_name: str, is_live: bool) -> str:
    general = f"{localization[u.language]['add'][1][0]} "
    name = channel_name if is_live else get_html_link(
        channel_url, channel_name)
    is_streaming = localization[u.language]['add'][1][2 if is_live else 3]
    game = f" {localization[u.language]['add'][1][4]} {game_name+'.'}" if (
        is_live and not game_name == 'Just Chatting') else ''
    title = f'\n{get_html_link(channel_url, live_title)}' if is_live else ''
    return f"{general}{name}{is_streaming}{game}{title}"


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
        print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
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
