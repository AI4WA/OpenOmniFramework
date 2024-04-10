from uuid import uuid4

from django.db import models

from authenticate.models import User

# Create your models here.


class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    llm_model_name = models.CharField(max_length=255, help_text="Model name")
    summary = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.llm_model_name


class ChatRecord(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=255,
        choices=[
            ("user", "User"),
            ("assistant", "Assistant"),
            ("system", "System"),
            ("function", "Function"),
        ],
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.message
