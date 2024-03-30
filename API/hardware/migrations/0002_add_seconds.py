# Generated by Django 4.2.8 on 2024-03-14 00:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hardware", "0001_init"),
    ]

    operations = [
        migrations.AddField(
            model_name="audiodata",
            name="translation_in_seconds",
            field=models.FloatField(
                default=0, help_text="The time taken to translate the audio"
            ),
            preserve_default=False,
        ),
    ]
