from django.contrib import admin
from telegram_bot.models import User, Message
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.conf import settings
from telegram_notification.tasks import broadcast_message
from telegram_bot.handlers.bot_handlers.utils import _send_message
from telegram_bot.forms import BroadcastForm


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'user_id', 'username', 'first_name', 'last_name',
        'language', 'deep_link',
        'created_at', 'updated_at', "is_blocked_bot",
    ]
    list_filter = ["is_blocked_bot", ]
    search_fields = ('username', 'user_id')
    actions = ['broadcast']

    @admin.action(description='Broadcast message to selected Users')
    def broadcast(self, request, queryset):
        """ Select users via check mark in django-admin panel, then select "Broadcast" to send message"""
        user_ids = queryset.values_list(
            'user_id', flat=True).distinct().iterator()

        if 'apply' in request.POST:
            broadcast_message_text = request.POST["broadcast_text"]

            if settings.DEBUG:
                for user_id in user_ids:
                    _send_message(
                        user_id=user_id,
                        text=broadcast_message_text,
                    )
                self.message_user(
                    request, f"Just broadcasted to {len(queryset)} users")
            else:
                broadcast_message.delay(
                    text=broadcast_message_text, user_ids=list(user_ids))
                self.message_user(
                    request, f"Broadcasting of {len(queryset)} messages has been started")

            return HttpResponseRedirect(request.get_full_path())
        else:
            form = BroadcastForm(initial={'_selected_action': user_ids})
            return render(
                request, "admin/broadcast_message.html", {
                    'form': form, 'title': u'Broadcast message'}
            )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'text', 'created_at')
    search_fields = ('user__username', 'text')
