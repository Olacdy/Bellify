from django.core.management import BaseCommand
from bellify_bot.handlers.bot_handlers.utils import check_twitch


class Command(BaseCommand):
    help = 'Checks all Twitch channels for a live stream'

    def handle(self, *args, **options):
        check_twitch()
