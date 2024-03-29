# Generated by Django 3.2.4 on 2021-09-02 08:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('screens', '0016_auto_20210826_2231'),
    ]

    operations = [
        migrations.AddField(
            model_name='source',
            name='playlists',
            field=models.ManyToManyField(blank=True, help_text='All sources that would be played by these playlists will be included in this one too.', related_name='sources', through='screens.PlaylistEntry', to='screens.Playlist'),
        ),
        migrations.AlterField(
            model_name='playlistrelation',
            name='super_list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='children_list', to='screens.playlist', verbose_name='Parent'),
        ),
    ]
