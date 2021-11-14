from celery import shared_task
from youtube.models import ChannelUserItem
from django.core.management import call_command
import telegram_bot.utils as utils
import urllib.parse


@shared_task
def notify_users(users, channel):
    lang_for_notifying = {
        'en':
            [
                ['New video from', 'is out!']
            ],
        'ru':
            [
                ['Новое видео на канале', 'уже вышло!']
            ]
    }
    for user in users:
        user_title = ChannelUserItem.objects.get(
            channel=channel, user=user) if ChannelUserItem.objects.get(
            channel=channel, user=user) else channel.title
        utils.send_message(
            user.external_id, f"{lang_for_notifying[user.language][0][0]} {user_title} {lang_for_notifying[user.language][0][1]}\n<a href=\"{channel.video_url}\">{urllib.parse.quote(channel.video_title)}</a>")
    return None


@shared_task
def check_channels():
    call_command("check_channels", )
