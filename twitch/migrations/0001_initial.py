# Generated by Django 4.0.6 on 2022-07-20 00:00

from django.db import migrations, models
import django.db.models.deletion
import twitch.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bellify_bot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TwitchChannel',
            fields=[
                ('channel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bellify_bot.channel')),
                ('channel_login', models.CharField(max_length=128)),
                ('game_name', models.CharField(blank=True, max_length=128, null=True)),
                ('thumbnail_url', models.URLField(blank=True, null=True)),
                ('thumbnail_image', models.ImageField(blank=True, null=True, upload_to=twitch.models.twitch_thumbnail_directory_path)),
            ],
            options={
                'verbose_name': 'Twitch Channel',
                'verbose_name_plural': 'Twitch Channels',
            },
            bases=('bellify_bot.channel',),
        ),
        migrations.CreateModel(
            name='TwitchChannelUserItem',
            fields=[
                ('channeluseritem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bellify_bot.channeluseritem')),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='twitch.twitchchannel')),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
            bases=('bellify_bot.channeluseritem',),
        ),
        migrations.AddField(
            model_name='twitchchannel',
            name='users',
            field=models.ManyToManyField(through='twitch.TwitchChannelUserItem', to='bellify_bot.user'),
        ),
    ]
