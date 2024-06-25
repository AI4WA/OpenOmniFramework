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
    name = models.CharField(
        max_length=100, help_text="A unique name to track the cluster of tasks"
    )
    task_name = models.CharField(
        max_length=100,
        choices=[
            ("quantization_llm", "Quantization LLM"),
            ("hf_llm", "HF LLM"),
            ("emotion_detection", "Emotion Detection"),
            ("speech2text", "Speech2Text"),
            ("text2speech", "Text2Speech"),
        ],
        help_text="Select the type of task",
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
    result_json = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text="The result of the task",
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @classmethod
    def create_task(cls, user, name, task_name, parameters, description=""):
        task = cls(
            user=user,
            name=name,
            task_name=task_name,
            parameters=parameters,
            description=description,
        )
        task.save()
        return task


class TaskWorker(models.Model):
    uuid = models.CharField(max_length=100, unique=True)
    task_name = models.CharField(max_length=100, blank=True, null=True)
    mac_address = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.uuid
