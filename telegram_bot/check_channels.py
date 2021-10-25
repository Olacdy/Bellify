from django.core.management import BaseCommand
from youtube.models import Channel
from .utils import send_message, check_for_new_video
import telegram_notification.tasks as tasks


class Command(BaseCommand):
    help = "Checks all channels for a new video"

    def handle(self, *args, **options):
        for channel in Channel.objects.all():
            check_for_new_video(channel)
