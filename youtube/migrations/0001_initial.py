# Generated by Django 4.0.7 on 2022-11-02 23:17

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bellify_bot', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='YouTubeChannel',
            fields=[
                ('channel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bellify_bot.channel')),
                ('deleted_livestreams', models.IntegerField(blank=True, default=-1, null=True)),
            ],
            options={
                'verbose_name': 'YouTube Channel',
                'verbose_name_plural': 'YouTube Channels',
            },
            bases=('bellify_bot.channel',),
        ),
        migrations.CreateModel(
            name='YouTubeVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('video_id', models.CharField(blank=True, max_length=20, null=True)),
                ('video_title', models.CharField(blank=True, max_length=256, null=True)),
                ('is_saved_livestream', models.BooleanField(blank=True, default=False, null=True)),
                ('is_reuploaded', models.BooleanField(blank=True, default=False, null=True)),
                ('added_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('published_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_basic_notified', models.BooleanField(blank=True, default=True, null=True)),
                ('is_premium_notified', models.BooleanField(blank=True, default=True, null=True)),
                ('iterations_skipped', models.PositiveSmallIntegerField(blank=True, default=0, null=True)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='videos', related_query_name='video', to='youtube.youtubechannel')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_%(app_label)s.%(class)s_set+', to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'YouTube Video',
                'verbose_name_plural': 'YouTube Videos',
            },
        ),
        migrations.CreateModel(
            name='YouTubeLivestream',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('livestream_id', models.CharField(blank=True, max_length=20, null=True)),
                ('livestream_title', models.CharField(blank=True, max_length=256, null=True)),
                ('is_notified', models.BooleanField(blank=True, default=True, null=True)),
                ('ended_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('is_checked_for_deleted', models.BooleanField(blank=True, default=False, null=True)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='livestreams', related_query_name='livestream', to='youtube.youtubechannel')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_%(app_label)s.%(class)s_set+', to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'YouTube Livestream',
                'verbose_name_plural': 'YouTube Livestreams',
            },
        ),
        migrations.CreateModel(
            name='YouTubeChannelUserItem',
            fields=[
                ('channeluseritem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bellify_bot.channeluseritem')),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='youtube.youtubechannel')),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
            bases=('bellify_bot.channeluseritem',),
        ),
        migrations.AddField(
            model_name='youtubechannel',
            name='users',
            field=models.ManyToManyField(through='youtube.YouTubeChannelUserItem', to='bellify_bot.user'),
        ),
    ]
