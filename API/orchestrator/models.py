from typing import Optional
from uuid import uuid4

from django.db import models

from authenticate.models import User
from orchestrator.chain.signals import completed_task


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
    track_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="The tracking ID of the task, will start with T-{cluster_name}-{id}",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @classmethod
    def create_task(
        cls,
        user: Optional[User],
        name: str,
        task_name: str,
        parameters: dict,
        description: str = "",
        track_id: Optional[str] = None,
    ):
        """
        Create a task
        Args:
            user (User): The user who created the task
            name (str): The name of the task
            task_name (str): The name of the task
            parameters (dict): The parameters for the task
            description (str): The description of the task
            track_id (str): The tracking ID of the task, will start with T-{cluster_name}-{id}

        Returns:

        """
        task = cls(
            user=user,
            name=name,
            task_name=task_name,
            parameters=parameters,
            description=description,
            track_id=track_id,
        )
        task.save()
        return task

    @staticmethod
    def init_track_id(name: str) -> str:
        """
        Initialize the track ID
        Args:
            name (str): The name of the task

        Returns:
            str: The track ID
        """
        uid = str(uuid4())
        # replace the - with ""
        uid = uid.replace("-", "")
        return f"T-{name}-{uid}"

    # override the save method, to call the chain
    def save(self, *args, **kwargs):
        # if it is updated, then we need to call the chain
        if self.result_status == "completed":
            completed_task.send(sender=self, data=self.__dict__)
        super().save(*args, **kwargs)


class TaskWorker(models.Model):
    uuid = models.CharField(max_length=100, unique=True)
    task_name = models.CharField(max_length=100, blank=True, null=True)
    mac_address = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.uuid
