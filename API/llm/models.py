from django.db import models

from authenticate.models import User


class LLMRequestRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    model_name = models.CharField(max_length=100)
    prompt = models.TextField()
    response = models.JSONField(default=dict, blank=True, null=True)
    task = models.CharField(max_length=100,
                            choices=[("chat-completion", "Chat Completion"), ("completion", "Completion"),
                                     ("create-embedding", "Create Embedding")], default="completion")
    completed_in_seconds = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.model_name} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
