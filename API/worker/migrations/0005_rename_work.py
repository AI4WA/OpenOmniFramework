# Generated by Django 4.2.8 on 2024-04-04 13:17

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("worker", "0004_add_task_type"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="GPUWorker",
            new_name="TaskWorker",
        ),
    ]