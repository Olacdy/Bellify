# Generated by Django 4.0.6 on 2022-08-10 14:15

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('twitch', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='twitchchannel',
            name='live_end_datetime',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
    ]
