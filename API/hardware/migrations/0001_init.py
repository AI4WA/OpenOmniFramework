# Generated by Django 4.2.8 on 2024-06-25 07:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
                    "logs",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="The logs of the text",
                        null=True,
                    ),
                ),
                (
                    "translation_in_seconds",
                    models.FloatField(
                        blank=True,
                        help_text="The time taken to translate the audio",
                        null=True,
                    ),
                ),
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
                    "pipeline_triggered",
                    models.BooleanField(
                        default=False, help_text="The pipeline is triggered or not"
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
            name="Text2Speech",
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
                    "text",
                    models.TextField(
                        blank=True, help_text="The text of the audio", null=True
                    ),
                ),
                (
                    "text2speech_file",
                    models.CharField(
                        blank=True,
                        help_text="The audio file",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "played",
                    models.BooleanField(
                        default=False, help_text="The audio file is played or not"
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
                (
                    "data_text",
                    models.ForeignKey(
                        blank=True,
                        help_text="The text data",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="text2speech",
                        to="hardware.datatext",
                    ),
                ),
                (
                    "home",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="text2speech",
                        to="hardware.home",
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
        migrations.CreateModel(
            name="HardWareDevice",
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
                    "mac_address",
                    models.CharField(
                        help_text="The mac address of the hardware device",
                        max_length=100,
                        unique=True,
                    ),
                ),
                (
                    "device_name",
                    models.CharField(
                        blank=True,
                        help_text="The name of the hardware device",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "device_type",
                    models.CharField(
                        blank=True,
                        help_text="The type of the hardware device",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="The description of the hardware device",
                        null=True,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="The created time of the hardware device",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="The updated time of the hardware device",
                    ),
                ),
                (
                    "home",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hardware_devices",
                        to="hardware.home",
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
                (
                    "home",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="emotion_detection",
                        to="hardware.home",
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
                (
                    "home",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="video",
                        to="hardware.home",
                    ),
                ),
            ],
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
    ]
