import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.views import View

from telegram_bot.bot import process_telegram_event

logger = logging.getLogger(__name__)


def index(request):
    return JsonResponse({"error": "!"})


class TelegramBotWebhookView(View):
    def post(self, request, *args, **kwargs):
        if settings.DEBUG:
            process_telegram_event(json.loads(request.body))
        else:
            process_telegram_event.delay(json.loads(request.body))
        return JsonResponse({"ok": "POST request processed"})

    def get(self, request, *args, **kwargs):
        return JsonResponse({"ok": "Get request received! But nothing done"})
