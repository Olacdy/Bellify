import urllib.parse

import telegram_bot.utils as utils
from django.core.management import call_command
from telegram_bot.localization import localization
from youtube.models import ChannelUserItem

from celery import shared_task


@shared_task
def notify_users(users, channel):
    for user in users:
        user_title = ChannelUserItem.objects.get(
            channel=channel, user=user) if ChannelUserItem.objects.get(
            channel=channel, user=user) else channel.title
        utils.send_message(
            user.external_id, f"{localization[user.language]['check_command'][4][0]} {user_title} {localization[user.language]['check_command'][4][0]}\n<a href=\"{channel.video_url}\">{urllib.parse.quote(channel.video_title)}</a>")
    return None


@shared_task
def check_channels():
    call_command("check_channels", )
