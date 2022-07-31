from django.contrib import admin

from youtube.models import YouTubeChannel, YouTubeChannelUserItem


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


@admin.register(YouTubeChannel)
class YouTubeChannelAdmin(admin.ModelAdmin):
    # TODO: finish admin
    inlines = [YouTubeChannelUserItemInline, ]
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
