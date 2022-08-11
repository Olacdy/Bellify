from django.contrib import admin
from django.utils.html import format_html

from utils.models import IsLivestreaming, IsDeletingLivestreams
from youtube.models import (YouTubeChannel, YouTubeChannelUserItem,
                            YouTubeDeletedVideo, YouTubeEndedLivestream,
                            YouTubeLivestream, YouTubeVideo)


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

    fields = ['video_id', 'video_title',
              'video_url', 'is_saved_livestream', ]
    readonly_fields = ['video_url', ]

    verbose_name = 'Video'
    verbose_name_plural = 'Videos'

    extra = 0

    def video_url(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.video_url)

    def has_add_permission(self, request, obj):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


class YouTubeLivestreamInline(admin.TabularInline):
    model = YouTubeLivestream

    fields = ['livestream_id', 'livestream_title',
              'livestream_url', ]
    readonly_fields = ['livestream_url', ]

    verbose_name = 'Live Stream'
    verbose_name_plural = 'Live Streams'

    extra = 0

    def livestream_url(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.livestream_url)

    def has_add_permission(self, request, obj):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


class YouTubeLivestreamAdminParent(admin.ModelAdmin):
    fields = ['created_at', 'channel', 'livestream_id', 'livestream_title',
              'livestream_url', ]
    readonly_fields = ['created_at', 'livestream_url', ]

    search_fields = ['livestream_title',
                     'livestream_id', 'channel__channel_title', ]
    list_display = ['livestream_title', 'channel', ]

    extra = 0

    def livestream_url(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.livestream_url)


class YouTubeVideoAdminParent(admin.ModelAdmin):
    readonly_fields = ['created_at', 'video_url', ]

    search_fields = ['video_title', 'video_id', 'channel__channel_title', ]

    list_filter = ['is_saved_livestream', ]
    list_display = ['video_title', 'channel', 'is_saved_livestream', ]

    extra = 0

    def video_url(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.video_url)


@admin.register(YouTubeVideo)
class YouTubeVideoAdmin(YouTubeVideoAdminParent):
    model = YouTubeVideo

    fields = ['created_at', 'channel', 'video_id', 'video_title',
              'video_url', 'is_saved_livestream', 'iterations_skipped', ]

    verbose_name = 'Video'
    verbose_name_plural = 'Videos'


@admin.register(YouTubeDeletedVideo)
class YouTubeDeletedVideoAdmin(YouTubeVideoAdminParent):
    model = YouTubeDeletedVideo

    fields = ['created_at', 'channel', 'video_id', 'video_title',
              'video_url', 'is_saved_livestream', 'is_counted_as_deleted_livestream', ]

    list_filter = ['is_saved_livestream', 'is_counted_as_deleted_livestream', ]
    list_display = ['video_title', 'channel',
                    'is_saved_livestream', 'is_counted_as_deleted_livestream', ]

    verbose_name = 'Deleted Video'
    verbose_name_plural = 'Deleted Videos'


@admin.register(YouTubeLivestream)
class YouTubeLivestreamAdmin(YouTubeLivestreamAdminParent):
    model = YouTubeLivestream

    verbose_name = 'Livestream'
    verbose_name_plural = 'Livestreams'


@admin.register(YouTubeEndedLivestream)
class YouTubeLivestreamAdmin(YouTubeLivestreamAdminParent):
    model = YouTubeEndedLivestream

    verbose_name = 'Ended Livestream'
    verbose_name_plural = 'Ended Livestreams'


@admin.register(YouTubeChannel)
class YouTubeChannelAdmin(admin.ModelAdmin):
    inlines = [YouTubeVideoInline, YouTubeLivestreamInline,
               YouTubeChannelUserItemInline, ]
    search_fields = ['channel_title', 'videos__video_title',
                     'livestreams__livestream_title', ]
    list_filter = [IsLivestreaming, IsDeletingLivestreams, ]
    list_display = ['channel_title', 'last_video',
                    'is_live', 'is_deleting_streams', ]
    # exclude = ['deleted_livestreams', ]

    def last_video(self, obj):
        return obj.last_video

    def is_live(self, obj):
        return obj.is_livestreaming

    def is_deleting_streams(self, obj):
        return obj.is_deleting_livestreams

    is_live.boolean = True
    is_deleting_streams.boolean = True
