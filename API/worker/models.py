from django.db import models

from authenticate.models import User


# Create your models here.
class Task(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        help_text="Select the user",
    )
    name = models.CharField(max_length=100)
    work_type = models.CharField(
        max_length=100,
        choices=[("llm", "LLM"), ("stt", "Speech2Text"), ("gpu", "GPU")],
        help_text="Select the type of work",
    )
    parameters = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text="Enter the parameters for the task",
    )
    result_status = models.CharField(
        max_length=100,
        choices=[
            ("pending", "Pending"),
            ("completed", "Completed"),
            ("failed", "Failed"),
            ("started", "Started"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @classmethod
    def create_task(cls, user, name, work_type, parameters, description=""):
        task = cls(
            user=user,
            name=name,
            work_type=work_type,
            parameters=parameters,
            description=description,
        )
        task.save()
        return task
