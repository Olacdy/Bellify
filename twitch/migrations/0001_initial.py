# Generated by Django 3.2.13 on 2022-05-05 23:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('telegram_bot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TwitchChannel',
            fields=[
                ('channel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='telegram_bot.channel')),
            ],
            options={
                'verbose_name': 'Twitch Channel',
                'verbose_name_plural': 'Twitch Channels',
            },
            bases=('telegram_bot.channel',),
        ),
        migrations.CreateModel(
            name='TwitchChannelUserItem',
            fields=[
                ('channeluseritem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='telegram_bot.channeluseritem')),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='twitch.twitchchannel')),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
            bases=('telegram_bot.channeluseritem',),
        ),
        migrations.AddField(
            model_name='twitchchannel',
            name='users',
            field=models.ManyToManyField(through='twitch.TwitchChannelUserItem', to='telegram_bot.User'),
        ),
    ]
