from django.db import models
from django.contrib.auth.models import User


class ChatHistory(models.Model):
    chat_uuid = models.UUIDField()
    user = models.CharField(max_length=100)
    message_type = models.CharField(max_length=100, default="user", choices=(("user", "User"), ("bot", "Bot")))
    message_content = models.TextField()
    model_name = models.CharField(max_length=100)
    model_params = models.JSONField(default=dict, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}/{self.message_type}: {self.message}"
