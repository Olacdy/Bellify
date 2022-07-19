import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from twitch.models import TwitchChannel

from bellify_bot.bot import process_telegram_event

logger = logging.getLogger(__name__)


class StreamPageView(View):
    template_name = "twitch/stream_page.html"

    def get(self, request, channel_login):
        try:
            channel = TwitchChannel.objects.get(channel_login=channel_login)
            return render(request, self.template_name, {'name': channel, 'title': channel.channel_title, 'description': channel.live_title, 'thumbnail_url': channel.thumbnail_url, 'video_url': channel.video_url, 'channel_url': channel.channel_url})
        except:
            return redirect('/')


class TelegramBotWebhookView(View):
    def post(self, request, *args, **kwargs):
        if settings.DEBUG:
            process_telegram_event(json.loads(request.body))
        else:
            process_telegram_event.delay(json.loads(request.body))
        return JsonResponse({"ok": "POST request processed"})

    def get(self, request, *args, **kwargs):
        return JsonResponse({"ok": "Get request received! But nothing done"})
