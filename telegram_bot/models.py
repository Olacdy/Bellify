from django.db import models


class Profile(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='ID of an user',
        unique=True,
    )
    name = models.TextField(
        verbose_name='User name'
    )
    language = models.CharField(
        max_length=3,
        default='eng'
    )
    menu = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    def __str__(self):
        return f'#{self.external_id} {self.name}'

    class Meta:
        verbose_name = 'User profile'
        verbose_name_plural = 'User profiles'


class Message(models.Model):
    profile = models.ForeignKey(
        to='telegram_bot.Profile',
        verbose_name='User name',
        on_delete=models.PROTECT,
    )
    text = models.TextField(
        verbose_name='Text',
    )
    created_at = models.DateTimeField(
        verbose_name='Recieve time',
        auto_now_add=True,
    )

    def __str__(self):
        return f'Message {self.pk} of {self.profile}'

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Message'
