# Generated by Django 4.2.8 on 2024-06-26 02:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("hardware", "0001_init"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="datatext",
            name="logs",
        ),
        migrations.RemoveField(
            model_name="datatext",
            name="translation_in_seconds",
        ),
    ]
