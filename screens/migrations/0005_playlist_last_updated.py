# Generated by Django 2.2.1 on 2019-07-11 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('screens', '0004_source_exclude_from_play_all'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
