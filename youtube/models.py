from typing import Optional

from django.db import models
from telegram_bot.models import User

from utils.models import nb


# Channel model
class Channel(models.Model):
    title = models.CharField(max_length=200)

    channel_id = models.CharField(max_length=200)
    channel_url = models.URLField()

    video_title = models.CharField(max_length=200, **nb)
    video_url = models.URLField(**nb)
    video_publication_date = models.DateTimeField(**nb)

    live_title = models.CharField(max_length=200, **nb)
    is_live = models.BooleanField(default=False, **nb)

    users = models.ManyToManyField(User, through='ChannelUserItem')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Channel'
        verbose_name_plural = 'Channels'


# Custom through model with title
class ChannelUserItem(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    channel_title = models.CharField(max_length=200, default='', **nb)
    is_muted = models.BooleanField(default=False, **nb)

    def __str__(self) -> str:
        return self.channel_title

    @classmethod
    def set_muted(cls, u: User, name: str) -> None:
        item = ChannelUserItem.objects.get(user=u, channel_title=name)
        item.is_muted = not item.is_muted
        item.save()
