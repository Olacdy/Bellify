# Generated by Django 4.0.7 on 2022-08-22 14:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='youtubevideo',
            name='added_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
