from django.db import models


class Patient(models.Model):
    uid = models.CharField(max_length=100)
    routine = models.CharField(
        max_length=200,
        help_text="The routine of the Patient. e.g.: medication, exercise, eating schedules...",
        null=True,
        blank=True,
    )
    family_condition = models.CharField(
        max_length=100,
        help_text="The health condition of the Patient. e.g.: family members, engaged time...",
        null=True,
        blank=True,
    )
    health_condition = models.CharField(
        max_length=100,
        help_text="The health condition of the Patient e.g.: medical history, chronic condition...",
        null=True,
        blank=True,
    )
    diet_preference = models.CharField(
        max_length=100,
        help_text="The diet preference of the Patient",
        null=True,
        blank=True,
    )
    hobby = models.CharField(
        max_length=100,
        help_text="The hobby of the Patient",
        null=True,
        blank=True,
    )
    personality = models.CharField(
        max_length=100,
        help_text="The personality of the Patient",
        null=True,
        blank=True,
    )
    additional_info = models.CharField(
        max_length=100,
        help_text="Additional information about the Patient",
        null=True,
        blank=True,
    )





