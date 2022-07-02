from django.conf import settings
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path('', RedirectView.as_view(url=settings.BELLIFY_LINK)),
    path(f'{settings.TG_WEBHOOK_ENDPOINT}/',
         csrf_exempt(views.TelegramBotWebhookView.as_view())),
]
