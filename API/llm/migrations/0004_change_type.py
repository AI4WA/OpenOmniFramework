# Generated by Django 4.2.8 on 2024-03-30 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("llm", "0003_add_success"),
    ]

    operations = [
        migrations.AlterField(
            model_name="llmrequestrecord",
            name="task",
            field=models.CharField(
                choices=[
                    ("chat_completion", "Chat Completion"),
                    ("completion", "Completion"),
                    ("create_embedding", "Create Embedding"),
                ],
                default="completion",
                max_length=100,
            ),
        ),
    ]
