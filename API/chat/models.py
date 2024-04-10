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

    def action_required(self):
        # get all chat records
        chat_records = ChatRecord.objects.filter(chat=self).order_by("created_at")
        # so if the first record is from the user, then we need to respond
        needed = chat_records.first().role == "user"
        messages = [
            {
                "role": record.role,
                "content": record.message,
            }
            for record in chat_records
        ]
        return needed, messages

    def respond(self, message):
        ChatRecord.objects.create(chat=self, role="assistant", message=message)

    def summary_required(self):
        """
        This method should return True if a summary is required
        Condition on summary is empty and there are more one message from the user
        Returns:

        """
        chat_records = ChatRecord.objects.filter(chat=self).order_by("created_at")
        needed = len(chat_records) > 0 and not self.summary
        prompt = "Summarize the conversation below: \n"
        for record in chat_records:
            prompt += f"{record.role}: {record.message}\n"
        return needed, prompt


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

    @property
    def uuid(self):
        return self.chat.uuid
