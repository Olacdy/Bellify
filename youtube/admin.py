from django.contrib import admin

from youtube.models import YouTubeChannel, YouTubeChannelUserItem


class YouTubeChannelUserItemInline(admin.TabularInline):
    model = YouTubeChannelUserItem
    extra = 1


@admin.register(YouTubeChannel)
class YouTubeChannelAdmin(admin.ModelAdmin):
    inlines = (YouTubeChannelUserItemInline,)
    list_display = ('channel_title', 'video_title', 'live_title')
