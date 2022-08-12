import time
from typing import Dict, List, Optional, Union, Tuple

from utils.general_utils import get_html_link, get_html_bold, _send_message, _from_celery_entities_to_entities, _from_celery_markup_to_markup
from utils.keyboards import get_notification_reply_markup
from django.core.management import call_command
from bellify_bot.localization import localization
from bellify_bot.models import User, ChannelUserItem

from celery.utils.log import get_task_logger
from bellify.celery import app

logger = get_task_logger(__name__)


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
