# Generated by Django 4.2.8 on 2024-06-26 09:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("hardware", "0002_add_trackid"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="emotiondetection",
            name="data_text",
        ),
        migrations.RemoveField(
            model_name="text2speech",
            name="data_text",
        ),
    ]
