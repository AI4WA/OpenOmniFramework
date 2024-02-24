# Generated by Django 5.0.2 on 2024-02-24 08:19

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AudioData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("uid", models.CharField(max_length=100)),
                (
                    "sequence_index",
                    models.IntegerField(help_text="The sequence index of the audio"),
                ),
                ("text", models.TextField(help_text="The text of the audio")),
                (
                    "audio_file",
                    models.CharField(help_text="The audio file", max_length=100),
                ),
                (
                    "start_time",
                    models.DateTimeField(help_text="The start time of the audio"),
                ),
                (
                    "end_time",
                    models.DateTimeField(help_text="The end time of the audio"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, help_text="The created time of the audio"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, help_text="The updated time of the audio"
                    ),
                ),
            ],
            options={
                "db_table": "audio_data",
                "unique_together": {("uid", "sequence_index")},
            },
        ),
    ]
