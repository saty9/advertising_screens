# Generated by Django 2.2.1 on 2019-07-13 16:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('artifax_id', models.IntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('artifax_id', models.IntegerField(unique=True)),
                ('venue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='room_schedules.Venue')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('organiser', models.CharField(max_length=200)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('artifax_id', models.IntegerField(unique=True)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='room_schedules.Room')),
            ],
        ),
    ]