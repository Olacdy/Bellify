from django_celery_beat.models import (
    IntervalSchedule,
    CrontabSchedule,
    SolarSchedule,
    ClockedSchedule,
    PeriodicTask,
)
from django.contrib import admin
from youtube.models import YoutubeChannel, YoutubeChannelUserItem


class YoutubeChannelUserItemInline(admin.TabularInline):
    model = YoutubeChannelUserItem
    extra = 1


@admin.register(YoutubeChannel)
class YoutubeChannelAdmin(admin.ModelAdmin):
    inlines = (YoutubeChannelUserItemInline,)
    list_display = ('title', 'video_title', 'is_live')


admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
