from django.core.management import BaseCommand
from youtube.models import Channel
from telegram_bot.handlers.bot_handlers.utils import send_message, check_for_new_video
import telegram_notification.tasks as tasks
import time


class Command(BaseCommand):
    help = "Checks all channels for a new video"

    def handle(self, *args, **options):
        for channel in Channel.objects.all():
            check_for_new_video(channel)
            time.sleep(0.5)
