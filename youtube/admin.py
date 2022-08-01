from django.contrib import admin
from django.utils.html import format_html

from youtube.models import YouTubeChannel, YouTubeChannelUserItem, YouTubeVideo


class YouTubeChannelUserItemInline(admin.TabularInline):
    model = YouTubeChannelUserItem

    verbose_name = 'User'
    verbose_name_plural = 'Users'

    extra = 0

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class YouTubeVideoInline(admin.TabularInline):
    model = YouTubeVideo

    fields = ['video_title', 'show_video_url', 'is_saved_livestream', ]
    readonly_fields = ['show_video_url']

    verbose_name = 'Video'
    verbose_name_plural = 'Videos'

    extra = 0

    def show_video_url(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.video_url)

    def has_add_permission(self, request, obj):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(YouTubeChannel)
class YouTubeChannelAdmin(admin.ModelAdmin):
    inlines = [YouTubeVideoInline, YouTubeChannelUserItemInline, ]
    # search_fields = ['channel_title', 'videos.video_title',
    #                  'livestreams.livestream_title', ]
    # list_filter = ['livestreams.is_live', 'livestreams.is_upcoming', ]
    # list_display = ['channel_title', 'videos.video_title',
    #                 'livestreams.live_title', 'livestreams.is_upcoming', ]
    # fieldsets = [
    #     [None, {'fields': ['channel_id', 'channel_url', 'channel_title']}],
    #     ['Video Info', {'fields': [
    #         'video_title', 'video_url', 'video_published']}],
    #     ['Live Info', {'fields': [
    #         'live_title', 'live_url', 'is_live', 'is_upcoming']}]
    # ]
