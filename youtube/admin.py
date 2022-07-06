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
        return True

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(YouTubeChannel)
class YouTubeChannelAdmin(admin.ModelAdmin):
    inlines = (YouTubeChannelUserItemInline,)
    list_display = ('channel_title', 'video_title', 'live_title')
