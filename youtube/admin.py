from django.contrib import admin

from youtube.models import YouTubeChannel, YouTubeChannelUserItem


class YouTubeChannelUserItemInline(admin.TabularInline):
    model = YouTubeChannelUserItem
    extra = 1


@admin.register(YouTubeChannel)
class YouTubeChannelAdmin(admin.ModelAdmin):
    inlines = (YouTubeChannelUserItemInline,)
    list_display = ('title', 'video_title', 'is_live')
