import time
from typing import Dict, List, Optional, Union

from utils.general_utils import get_html_link, get_html_bold, _send_message, _from_celery_entities_to_entities, _from_celery_markup_to_markup
from utils.keyboards import get_notification_reply_markup
from django.core.management import call_command
from bellify_bot.localization import localization
from bellify_bot.models import User, ChannelUserItem

from celery.utils.log import get_task_logger
from bellify.celery import app

logger = get_task_logger(__name__)


@app.task(ignore_result=True)
def notify_users(user_ids: List[int], content_info: dict) -> None:
    def _get_message(user_title: str, channel_info: dict, user: User):
        user_title = get_html_bold(user_title)

        if content_info.get('is_live', False):
            notification = f" — {localization[user.language]['notification'][1] if not 'game_name' in channel_info or channel_info['game_name'] == 'Just Chatting' else localization[user.language]['notification'][2]+' '+channel_info['game_name']+'!'}"
            href = f"{get_html_link(url=channel_info['preview_url']) if 'preview_url' in channel_info and not user.is_twitch_thumbnail_disabled else get_html_link(url=channel_info['url'])}"
            return f"{user_title}{notification}{href}"
        else:
            if channel_info['is_reuploaded']:
                notification = f" — {localization[user.language]['notification'][3]}"
            elif channel_info['is_saved_livestream']:
                notification = f" — {localization[user.language]['notification'][4]}{(' ' + localization[user.language]['notification'][5]) if channel_info['might_be_deleted'] else ''}"
            else:
                notification = f" — {localization[user.language]['notification'][0]}"
            href = f"{get_html_link(channel_info['url'])}"
            return f"{user_title}{notification}{href}"

    for user_id in user_ids:
        user: User = User.objects.get(user_id=user_id)
        item: ChannelUserItem = ChannelUserItem.get_user_channel_by_id(
            user, content_info['id'])
        user_title, is_muted = item.message_title_and_type, item.is_muted
        if content_info.get('is_live', False):
            _send_message(
                user_id, _get_message(
                    user_title, content_info, user),
                reply_markup=get_notification_reply_markup(
                    content_info['title'], content_info['url']),
                disable_notification=is_muted)
        else:
            _send_message(
                user_id, _get_message(
                    user_title, content_info, user),
                reply_markup=get_notification_reply_markup(
                    content_info['title'], content_info['url']),
                disable_notification=is_muted)


@app.task(ignore_result=True)
def broadcast_message(
    user_ids: List[Union[str, int]],
    text: str,
    entities: Optional[List[Dict]] = None,
    reply_markup: Optional[List[List[Dict]]] = None,
    sleep_between: float = 0.1,
    parse_mode='HTML',
) -> None:
    """ It's used to broadcast message to big amount of users """
    logger.info(f"Going to send message: '{text}' to {len(user_ids)} users")

    entities_ = _from_celery_entities_to_entities(entities)
    reply_markup_ = _from_celery_markup_to_markup(reply_markup)
    for user_id in user_ids:
        try:
            _send_message(
                user_id=user_id,
                text=text,
                entities=entities_,
                parse_mode=parse_mode,
                reply_markup=reply_markup_,
            )
            logger.info(f'Broadcast message was sent to {user_id}')
        except Exception as e:
            logger.error(f'Failed to send message to {user_id}, reason: {e}')
        time.sleep(max(sleep_between, 0.1))

    logger.info('Broadcast finished!')


@app.task(ignore_result=True)
def check_youtube():
    call_command('check_youtube', )


@app.task(ignore_result=True)
def check_twitch():
    call_command('check_twitch',)
