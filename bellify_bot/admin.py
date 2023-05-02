from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django_celery_beat.models import (ClockedSchedule, CrontabSchedule,
                                       IntervalSchedule, PeriodicTask,
                                       SolarSchedule)

from bellify.tasks import broadcast_message
from bellify_bot.forms import BroadcastForm
from bellify_bot.models import User, Order
from twitch.models import TwitchChannelUserItem
from utils.general_utils import _send_message
from youtube.models import YouTubeChannelUserItem


class YouTubeChannelsInline(admin.TabularInline):
    model = YouTubeChannelUserItem
    readonly_fields = ['channel', 'is_muted']

    verbose_name = 'YouTube Channel'
    verbose_name_plural = 'YouTube Channels'

    extra = 0

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class TwitchChannelsInline(admin.TabularInline):
    model = TwitchChannelUserItem
    readonly_fields = ['channel', 'is_muted']

    verbose_name = 'Twitch Channel'
    verbose_name_plural = 'Twitch Channels'

    extra = 0

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [
        YouTubeChannelsInline,
        TwitchChannelsInline,
    ]
    list_display = ['name', 'username', 'first_name',
                    'last_name', 'language', 'max_youtube_channels_number', 'max_twitch_channels_number', 'status', 'has_added_channels', ]
    list_filter = ['is_blocked_bot', 'language', 'status', ]
    search_fields = ['username', 'user_id', ]
    actions = ['broadcast', ]
    fields = ['user_id', 'username', 'first_name', 'last_name', 'deep_link', 'status',
              'language', 'max_youtube_channels_number', 'max_twitch_channels_number', 'is_tutorial_finished', 'is_admin', ]

    def name(self, obj):
        return obj.tg_str

    def has_added_channels(self, obj):
        return bool(obj.channeluseritem_set.all().count() > 0)

    @admin.action(description='Broadcast message to selected Users')
    def broadcast(self, request, queryset):
        """ Select users via check mark in django-admin panel, then select "Broadcast" to send message"""
        user_ids = queryset.values_list(
            'user_id', flat=True).distinct().iterator()

        if 'apply' in request.POST:
            broadcast_message_text = request.POST['broadcast_text']

            if settings.DEBUG:
                for user_id in user_ids:
                    _send_message(
                        user_id=user_id,
                        text=broadcast_message_text,
                    )
                self.message_user(
                    request, f'Just broadcasted to {len(queryset)} users')
            else:
                broadcast_message.delay(
                    text=broadcast_message_text, user_ids=list(user_ids))
                self.message_user(
                    request, f'Broadcasting of {len(queryset)} messages has been started')

            return HttpResponseRedirect(request.get_full_path())
        else:
            form = BroadcastForm(initial={'_selected_action': user_ids})
            return render(
                request, 'admin/broadcast_message.html', {
                    'form': form, 'title': u'Broadcast message'}
            )

    has_added_channels.boolean = True


def get_app_list(self, request):
    app_dict = self._build_app_dict(request)
    app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
    for app in app_list:
        if app['app_label'] == 'youtube':
            ordering = {
                'YouTube Channels': 1,
                'YouTube Videos': 2,
                'YouTube Livestreams': 3,
            }
            app['models'].sort(key=lambda x: ordering[x['name']])

    return app_list


admin.AdminSite.get_app_list = get_app_list
admin.site.register(Order)
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
