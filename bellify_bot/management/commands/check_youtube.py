from django.core.management import BaseCommand
from bellify_bot.handlers.notification_handler import check_youtube


class Command(BaseCommand):
    help = 'Checks all Youtube channels for a new video or livestream'

    def handle(self, *args, **options):
        check_youtube()
