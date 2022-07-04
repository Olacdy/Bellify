from django.contrib import admin

from twitch.models import TwitchChannel, TwitchChannelUserItem


class TwitchChannelUserItemInline(admin.TabularInline):
    model = TwitchChannelUserItem
    extra = 1


@admin.register(TwitchChannel)
class TwitchChannelAdmin(admin.ModelAdmin):
    inlines = (TwitchChannelUserItemInline,)
    list_display = ('channel_title', 'live_title', 'is_live')
