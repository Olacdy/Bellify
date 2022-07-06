from django.contrib import admin

from twitch.models import TwitchChannel, TwitchChannelUserItem


class TwitchChannelUserItemInline(admin.TabularInline):
    model = TwitchChannelUserItem
    extra = 0

    verbose_name = 'User'
    verbose_name_plural = 'Users'

    extra = 0

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TwitchChannel)
class TwitchChannelAdmin(admin.ModelAdmin):
    inlines = (TwitchChannelUserItemInline,)
    list_display = ('channel_title', 'live_title', 'is_live')
