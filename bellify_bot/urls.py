from django.conf import settings
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path('', views.LandingPageView.as_view()),
    # path('', RedirectView.as_view(url=settings.BELLIFY_LINK)),
    path('twitch/<channel_login>/<date>', views.StreamPageView.as_view()),
    path(f'{settings.TG_WEBHOOK_ENDPOINT}/',
         csrf_exempt(views.TelegramBotWebhookView.as_view())),
]
