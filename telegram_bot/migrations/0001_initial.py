# Generated by Django 3.2.13 on 2022-05-02 23:52

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
                ('language', models.CharField(blank=True,
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
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                 to='telegram_bot.user', verbose_name='User name')),
            ],
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Message',
            },
        ),
        migrations.RunPython(create_initial_superuser)
    ]
