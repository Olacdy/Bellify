from django.core.management import BaseCommand
from bellify_bot.handlers.bot_handlers.utils import check_for_live_youtube


class Command(BaseCommand):
    help = "Checks all Premium Youtube channels for a live stream"

    def handle(self, *args, **options):
        check_for_live_youtube()
