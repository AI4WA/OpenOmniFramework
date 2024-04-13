# Generated by Django 4.2.8 on 2024-04-04 07:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("worker", "0002_add_task_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="GPUWorker",
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
                ("uuid", models.CharField(max_length=100, unique=True)),
                (
                    "mac_address",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
