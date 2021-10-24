from django.contrib import admin
from .models import Channel, ChannelUserItem


class ChannelUserItemInline(admin.TabularInline):
    model = ChannelUserItem
    extra = 1


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    inlines = (ChannelUserItemInline,)
    list_display = ('title', 'channel_id', 'video_title',
                    'video_publication_date')
