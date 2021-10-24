# Generated by Django 3.2.8 on 2021-10-24 14:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('telegram_profile', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('channel_id', models.CharField(max_length=100)),
                ('channel_url', models.URLField()),
                ('video_title', models.CharField(max_length=150)),
                ('video_url', models.URLField()),
                ('video_publication_date', models.DateTimeField()),
            ],
            options={
                'verbose_name': 'Channel',
                'verbose_name_plural': 'Channels',
            },
        ),
        migrations.CreateModel(
            name='ChannelUserItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_title', models.CharField(default='', max_length=100)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='youtube.channel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='telegram_profile.profile')),
            ],
        ),
        migrations.AddField(
            model_name='channel',
            name='users',
            field=models.ManyToManyField(through='youtube.ChannelUserItem', to='telegram_profile.Profile'),
        ),
    ]
