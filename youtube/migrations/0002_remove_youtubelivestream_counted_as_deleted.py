# Generated by Django 4.0.7 on 2022-08-22 09:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('youtube', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='youtubelivestream',
            name='counted_as_deleted',
        ),
    ]
