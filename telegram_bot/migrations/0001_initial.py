# Generated by Django 3.2.13 on 2022-05-05 23:04

from django.db import migrations, models
import django.db.models.deletion
from django.contrib.auth import get_user_model


def create_initial_superuser(apps, schema_editor):
    User = get_user_model()
    User.objects.create_superuser(
        'admin', 'admin@admin.com', 'admin')


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('created_at', models.DateTimeField(
                    auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user_id', models.PositiveBigIntegerField(
                    primary_key=True, serialize=False)),
                ('username', models.CharField(blank=True, max_length=64, null=True)),
                ('first_name', models.CharField(
                    blank=True, max_length=256, null=True)),
                ('last_name', models.CharField(
                    blank=True, max_length=256, null=True)),
                ('language', models.CharField(blank=True, default=None,
                 help_text="Telegram client's lang", max_length=8, null=True)),
                ('deep_link', models.CharField(blank=True, max_length=64, null=True)),
                ('menu', models.CharField(blank=True, max_length=64, null=True)),
                ('status', models.CharField(blank=True, choices=[
                 ('B', 'Basic'), ('P', 'Premium')], default='B', max_length=1, null=True)),
                ('max_youtube_channels_number', models.PositiveIntegerField(
                    blank=True, default=3, null=True)),
                ('max_twitch_channels_number', models.PositiveIntegerField(
                    blank=True, default=0, null=True)),
                ('is_blocked_bot', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE,
                 related_name='polymorphic_telegram_bot.user_set+', to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'Telegram User',
                'verbose_name_plural': 'Telegram Users',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(
                    auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('text', models.TextField(verbose_name='Text')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE,
                 related_name='polymorphic_telegram_bot.message_set+', to='contenttypes.contenttype')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                 to='telegram_bot.user', verbose_name='User name')),
            ],
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Message',
            },
        ),
        migrations.CreateModel(
            name='ChannelUserItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(
                    auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('channel_title', models.CharField(
                    blank=True, default='', max_length=200, null=True)),
                ('is_muted', models.BooleanField(default=False)),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE,
                 related_name='polymorphic_telegram_bot.channeluseritem_set+', to='contenttypes.contenttype')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='telegram_bot.user')),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(
                    auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=256)),
                ('channel_id', models.CharField(max_length=128, unique=True)),
                ('channel_url', models.URLField(unique=True)),
                ('live_url', models.URLField(blank=True, null=True)),
                ('live_title', models.CharField(
                    blank=True, max_length=256, null=True)),
                ('is_live', models.BooleanField(
                    blank=True, default=False, null=True)),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE,
                 related_name='polymorphic_telegram_bot.channel_set+', to='contenttypes.contenttype')),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
        migrations.RunPython(create_initial_superuser)
    ]
