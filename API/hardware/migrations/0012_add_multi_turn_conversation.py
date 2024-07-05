# Generated by Django 4.2.8 on 2024-07-05 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hardware", "0011_add_tag"),
    ]

    operations = [
        migrations.AddField(
            model_name="datamultimodalconversation",
            name="multi_turns_annotations",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="The annotations of the multi-turns",
                null=True,
            ),
        ),
    ]
