from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from twitch.models import TwitchChannel, TwitchChannelUserItem


class TwitchChannelUserItemInline(admin.TabularInline):
    model = TwitchChannelUserItem

    fields = ['username', 'channel_title', 'is_muted', ]
    readonly_fields = ['username', ]

    verbose_name = 'User'
    verbose_name_plural = 'Users'

    extra = 0

    def username(self, obj):
        return mark_safe(f'<a href="{reverse("admin:bellify_bot_user_change", args=(obj.user_id,))}">{obj.user.tg_str}</a>')

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TwitchChannel)
class TwitchChannelAdmin(admin.ModelAdmin):
    inlines = [TwitchChannelUserItemInline, ]
    search_fields = ['channel_title', 'live_title', ]
    list_filter = ['is_live', ]
    list_display = ['channel_title', 'live_title', 'is_live']
    fieldsets = [
        [None, {'fields': ['channel_id', 'channel_url',
                           'channel_title', 'channel_login']}],
        ['Live Info', {'fields': [
            'live_title', 'game_name', 'thumbnail_url', 'thumbnail_image', 'is_live', 'live_end_datetime']}]
    ]
