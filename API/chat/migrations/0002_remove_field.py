# Generated by Django 4.2.8 on 2024-04-10 02:43

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0001_init_chat"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="chat",
            name="message",
        ),
    ]