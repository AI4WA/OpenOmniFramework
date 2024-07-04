# Generated by Django 4.2.8 on 2024-07-04 04:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hardware", "0008_add_track_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="contextemotiondetection",
            name="annotations",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="The annotations of the emotion detection",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="datamultimodalconversation",
            name="annotations",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="The annotations of the emotion detection",
                null=True,
            ),
        ),
    ]