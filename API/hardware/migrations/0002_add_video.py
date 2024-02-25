# Generated by Django 4.2.8 on 2024-02-24 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hardware', '0001_add_audio'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=100)),
                ('video_file', models.CharField(help_text='The video file', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The created time of the video')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='The updated time of the video')),
            ],
            options={
                'db_table': 'video_data',
            },
        ),
    ]