from django.contrib import admin

# Register your models here.
from chat.models import Chat, ChatRecord


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_filter = ("llm_model_name",)
    search_fields = ("llm_model_name",)
    list_display = ("user", "uuid", "llm_model_name", "created_at", "updated_at")


@admin.register(ChatRecord)
class ChatRecordAdmin(admin.ModelAdmin):
    list_filter = ("role",)
    search_fields = ("message",)
    list_display = ("role", "message", "uuid", "created_at", "updated_at")
