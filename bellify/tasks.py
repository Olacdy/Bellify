import time
from typing import Dict, List, Optional, Union

from utils.general_utils import get_twitch_channel_message, _send_message, _from_celery_entities_to_entities, _from_celery_markup_to_markup
from utils.keyboards import _get_notification_reply_markup
from django.core.management import call_command
from bellify_bot.localization import localization
from bellify_bot.models import User, ChannelUserItem

from celery.utils.log import get_task_logger
from bellify.celery import app

logger = get_task_logger(__name__)


@app.task(ignore_result=True)
def notify_users(users: List[User], channel_info: dict, live: Optional[bool] = False) -> None:
    for u in users:
        item = ChannelUserItem.get_user_channel_by_id(
            u, channel_info['id'])
        user_title, is_muted = item.channel_title, item.is_muted
        if not live:
            _send_message(
                u.user_id, f"{localization[u.language]['notification'][0][0]} {user_title} {localization[u.language]['notification'][0][1]}\n<a href=\"{channel_info['url']}\">{channel_info['title']}</a>",
                reply_markup=_get_notification_reply_markup(
                    channel_info['title'], channel_info['url']),
                disable_notification=not is_muted)
        else:
            _send_message(
                u.user_id, f"{user_title} {localization[u.language]['notification'][1]} {localization[u.language]['notification'][3]+channel_info['game_name'] if 'game_name' in channel_info else ''}\n<a href=\"{channel_info['url']}\">{channel_info['title']}</a>",
                reply_markup=_get_notification_reply_markup(
                    channel_info['title'], channel_info['url']),
                disable_notification=not is_muted)


@app.task(ignore_result=True)
def broadcast_message(
    user_ids: List[Union[str, int]],
    text: str,
    entities: Optional[List[Dict]] = None,
    reply_markup: Optional[List[List[Dict]]] = None,
    sleep_between: float = 0.2,
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
            logger.info(f"Broadcast message was sent to {user_id}")
        except Exception as e:
            logger.error(f"Failed to send message to {user_id}, reason: {e}")
        time.sleep(max(sleep_between, 0.1))

    logger.info("Broadcast finished!")


@app.task(ignore_result=True)
def check_channels_for_video_youtube():
    call_command("check_channels_for_video_youtube", )


@app.task(ignore_result=True)
def check_channels_for_live_stream_youtube():
    call_command("check_channels_for_live_stream_youtube", )


@app.task(ignore_result=True)
def check_channels_for_live_stream_twitch():
    call_command("check_channels_for_live_stream_twitch",)
