# Generated by Django 4.2.8 on 2024-03-27 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Patient",
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
                ("uid", models.CharField(max_length=100)),
                (
                    "routine",
                    models.CharField(
                        blank=True,
                        help_text="The routine of the Patient. e.g.: medication, exercise, eating schedules...",
                        max_length=200,
                        null=True,
                    ),
                ),
                (
                    "family_condition",
                    models.CharField(
                        blank=True,
                        help_text="The health condition of the Patient. e.g.: family members, engaged time...",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "health_condition",
                    models.CharField(
                        blank=True,
                        help_text="The health condition of the Patient e.g.: medical history, chronic condition...",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "diet_preference",
                    models.CharField(
                        blank=True,
                        help_text="The diet preference of the Patient",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "hobby",
                    models.CharField(
                        blank=True,
                        help_text="The hobby of the Patient",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "personality",
                    models.CharField(
                        blank=True,
                        help_text="The personality of the Patient",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "additional_info",
                    models.CharField(
                        blank=True,
                        help_text="Additional information about the Patient",
                        max_length=100,
                        null=True,
                    ),
                ),
            ],
        ),
    ]
