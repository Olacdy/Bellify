import json
import logging

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from bellify.celery import app
from twitch.models import TwitchChannel

logger = logging.getLogger(__name__)


class LandingPageView(View):
    template_name = 'index.html'

    def get(self, request):
        return render(request, self.template_name)


class StreamPageView(View):
    template_name = 'twitch/stream_page.html'

    def get(self, request, channel_login, date):
        try:
            channel = TwitchChannel.objects.get(channel_login=channel_login)
            if channel.is_live:
                return render(request, self.template_name, {'channel_title': channel.channel_title, 'channel_login': channel.channel_login, 'description': channel.live_title, 'thumbnail_url': channel.thumbnail})
            raise
        except:
            return redirect('/')


class TelegramBotWebhookView(View):
    def post(self, request, *args, **kwargs):
        app.send_task('process_telegram_event', args=[
            json.loads(request.body)], queue='telegram_events')
        return JsonResponse({'ok': 'POST request processed'})

    def get(self, request, *args, **kwargs):
        return JsonResponse({'ok': 'Get request received! But nothing done'})
