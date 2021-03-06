# Generated by Django 2.2.1 on 2019-07-08 17:24

from django.db import migrations, models
import django.db.models.deletion
import recurrence.fields
import screens.models.source


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('is_default', models.BooleanField(default=False)),
                ('default_playlist', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='screens.Playlist')),
            ],
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('IMG', 'Image'), (' VID', 'Video'), ('FRM', 'Yearly')], max_length=3)),
                ('name', models.TextField()),
                ('file', models.FileField(null=True, upload_to=screens.models.source.get_file_path)),
                ('url', models.URLField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Screen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('ip', models.GenericIPAddressField()),
                ('schedule', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='screens.Schedule')),
            ],
        ),
        migrations.CreateModel(
            name='ScheduleRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('starts', models.DateField()),
                ('occurrences', recurrence.fields.RecurrenceField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('priority', models.IntegerField()),
                ('playlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='screens.Playlist')),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='screens.Schedule')),
            ],
        ),
        migrations.CreateModel(
            name='SchedulePart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('priority', models.IntegerField()),
                ('playlist', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='screens.Playlist')),
                ('schedule_rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='screens.ScheduleRule')),
            ],
        ),
        migrations.CreateModel(
            name='PlaylistEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('playlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='screens.Playlist')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='screens.Source')),
            ],
        ),
    ]
