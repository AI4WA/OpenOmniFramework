# Generated by Django 4.2.8 on 2024-02-28 04:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('llm', '0001_add_records'),
    ]

    operations = [
        migrations.AlterField(
            model_name='llmrequestrecord',
            name='response',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]
