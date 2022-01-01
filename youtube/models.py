from django.db import models
from telegram_bot.models import Profile


# Channel model
class Channel(models.Model):
    title = models.CharField(max_length=200)
    channel_id = models.CharField(max_length=200)
    channel_url = models.URLField()
    video_title = models.CharField(max_length=200)
    video_url = models.URLField()
    video_publication_date = models.DateTimeField()
    users = models.ManyToManyField(Profile, through='ChannelUserItem')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Channel'
        verbose_name_plural = 'Channels'


# Custom through model with title
class ChannelUserItem(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    channel_title = models.CharField(max_length=200, default='')

    def __str__(self) -> str:
        return self.channel_title
