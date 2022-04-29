import asyncio
import platform

from django.core.management import BaseCommand
from telegram_bot.handlers.bot_handlers.utils import check_for_new_video


class Command(BaseCommand):
    help = "Checks all Youtube channels for a new video"

    def handle(self, *args, **options):
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(check_for_new_video())
