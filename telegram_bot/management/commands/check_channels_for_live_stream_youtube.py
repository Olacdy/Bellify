import asyncio
import platform

from django.core.management import BaseCommand
from telegram_bot.handlers.bot_handlers.utils import check_for_live_stream_youtube


class Command(BaseCommand):
    help = "Checks all Premium Youtube channels for a live stream"

    def handle(self, *args, **options):
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(check_for_live_stream_youtube())
