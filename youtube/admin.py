from django_celery_beat.models import (
    IntervalSchedule,
    CrontabSchedule,
    SolarSchedule,
    ClockedSchedule,
    PeriodicTask,
)
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


admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
