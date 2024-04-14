# Generated by Django 4.2.8 on 2024-04-11 12:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("hardware", "0007_add_react"),
    ]

    operations = [
        migrations.CreateModel(
            name="DataAudio",
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
                (
                    "uid",
                    models.CharField(
                        help_text="the uid of the audio acquire session", max_length=100
                    ),
                ),
                (
                    "hardware_device_mac_address",
                    models.CharField(
                        blank=True,
                        help_text="The mac address of the hardware device",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "sequence_index",
                    models.IntegerField(help_text="The sequence index of the audio"),
                ),
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
                    "translation_in_seconds",
                    models.FloatField(
                        help_text="The time taken to translate the audio"
                    ),
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
        ),
        migrations.CreateModel(
            name="DataText",
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
                ("text", models.TextField(help_text="The text of the audio")),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, help_text="The created time of the text"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, help_text="The updated time of the text"
                    ),
                ),
                (
                    "model_name",
                    models.CharField(
                        blank=True,
                        default="whisper",
                        help_text="The name of the model",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "audio",
                    models.ForeignKey(
                        help_text="The audio data",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="text",
                        to="hardware.dataaudio",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DataVideo",
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
                (
                    "uid",
                    models.CharField(
                        help_text="the uid of the video acquire session, link back to client logs",
                        max_length=100,
                    ),
                ),
                (
                    "hardware_device_mac_address",
                    models.CharField(
                        blank=True,
                        help_text="The mac address of the hardware device",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "video_file",
                    models.CharField(help_text="The video file", max_length=100),
                ),
                (
                    "video_record_minute",
                    models.DateTimeField(
                        blank=True, help_text="The minute of the video", null=True
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, help_text="The created time of the video"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, help_text="The updated time of the video"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EmotionDetection",
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
                (
                    "result",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="The emotion result of the text",
                        null=True,
                    ),
                ),
                (
                    "logs",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="The logs of the emotion detection",
                        null=True,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="The created time of the emotion detection",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="The updated time of the emotion detection",
                    ),
                ),
                (
                    "data_text",
                    models.ForeignKey(
                        help_text="The text data",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="emotion_detection",
                        to="hardware.datatext",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Home",
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
                (
                    "name",
                    models.CharField(
                        default="Blue Boat House",
                        help_text="The name of the home",
                        max_length=100,
                    ),
                ),
                (
                    "address",
                    models.CharField(
                        default="1 Kings Park Ave, Crawley WA 6009",
                        help_text="The address of the home",
                        max_length=100,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LLMResponse",
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
                (
                    "messages",
                    models.JSONField(
                        blank=True,
                        default=list,
                        help_text="The messages of the llm response",
                        null=True,
                    ),
                ),
                (
                    "result",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="The llm result of the text",
                        null=True,
                    ),
                ),
                (
                    "logs",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="The logs of the llm response",
                        null=True,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="The created time of the llm response",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, help_text="The updated time of the llm response"
                    ),
                ),
                (
                    "data_text",
                    models.ForeignKey(
                        help_text="The text data",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="llm_response",
                        to="hardware.datatext",
                    ),
                ),
                (
                    "home",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="llm_response",
                        to="hardware.home",
                    ),
                ),
            ],
        ),
        migrations.AlterUniqueTogether(
            name="audiodata",
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name="reactiontoaudio",
            name="audio",
        ),
        migrations.DeleteModel(
            name="VideoData",
        ),
        migrations.RenameField(
            model_name="text2speech",
            old_name="audio_file",
            new_name="text2speech_file",
        ),
        migrations.RemoveField(
            model_name="text2speech",
            name="spoken",
        ),
        migrations.AddField(
            model_name="text2speech",
            name="played",
            field=models.BooleanField(
                default=False, help_text="The audio file is played or not"
            ),
        ),
        migrations.AlterModelTable(
            name="text2speech",
            table=None,
        ),
        migrations.DeleteModel(
            name="AudioData",
        ),
        migrations.DeleteModel(
            name="ReactionToAudio",
        ),
        migrations.AddField(
            model_name="emotiondetection",
            name="home",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="emotion_detection",
                to="hardware.home",
            ),
        ),
        migrations.AddField(
            model_name="datavideo",
            name="home",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="video",
                to="hardware.home",
            ),
        ),
        migrations.AddField(
            model_name="datatext",
            name="home",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="text",
                to="hardware.home",
            ),
        ),
        migrations.AddField(
            model_name="dataaudio",
            name="home",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="audio",
                to="hardware.home",
            ),
        ),
        migrations.AddField(
            model_name="hardwaredevice",
            name="home",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="hardware_devices",
                to="hardware.home",
            ),
        ),
        migrations.AddField(
            model_name="text2speech",
            name="data_text",
            field=models.ForeignKey(
                blank=True,
                help_text="The text data",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="text2speech",
                to="hardware.datatext",
            ),
        ),
        migrations.AddField(
            model_name="text2speech",
            name="home",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="text2speech",
                to="hardware.home",
            ),
        ),
    ]