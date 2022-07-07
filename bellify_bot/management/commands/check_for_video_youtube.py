from django.core.management import BaseCommand
from bellify_bot.handlers.bot_handlers.utils import check_for_video_youtube


class Command(BaseCommand):
    help = "Checks all Youtube channels for a new video"

    def handle(self, *args, **options):
        check_for_video_youtube()
