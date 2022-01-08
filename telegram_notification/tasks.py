import time
import urllib.parse
from typing import Dict, List, Optional, Union

import telegram_bot.handlers.bot_handlers.utils as utils
from telegram_notification.celery import app
from django.core.management import call_command
from telegram_bot.localization import localization
from youtube.models import ChannelUserItem

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def notify_users(users, channel):
    for user in users:
        user_title = ChannelUserItem.objects.get(
            channel=channel, user=user) if ChannelUserItem.objects.get(
            channel=channel, user=user) else channel.title
        utils._send_message(
            user.user_id, f"{localization[user.language]['check_command'][4][0]} {user_title} {localization[user.language]['check_command'][4][1]}\n<a href=\"{channel.video_url}\">{urllib.parse.quote(channel.video_title)}</a>")


@app.task(ignore_result=True)
def broadcast_message(
    user_ids: List[Union[str, int]],
    text: str,
    entities: Optional[List[Dict]] = None,
    reply_markup: Optional[List[List[Dict]]] = None,
    sleep_between: float = 0.4,
    parse_mode='HTML',
) -> None:
    """ It's used to broadcast message to big amount of users """
    logger.info(f"Going to send message: '{text}' to {len(user_ids)} users")

    entities_ = utils._from_celery_entities_to_entities(entities)
    reply_markup_ = utils._from_celery_markup_to_markup(reply_markup)
    for user_id in user_ids:
        try:
            utils._send_message(
                user_id=user_id,
                text=text,
                entities=entities_,
                parse_mode=parse_mode,
                reply_markup=reply_markup_,
            )
            logger.info(f"Broadcast message was sent to {user_id}")
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}, reason: {e}")
        time.sleep(max(sleep_between, 0.1))

    logger.info("Broadcast finished!")


@shared_task
def check_channels():
    call_command("check_channels", )
