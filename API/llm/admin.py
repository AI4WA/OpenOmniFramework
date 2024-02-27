from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportModelAdmin
from llm.models import ChatHistory


@admin.register(ChatHistory)
class ChatHistoryAdmin(ImportExportModelAdmin):
    list_display = (
    "id", "chat_uuid", "user", "message_type", "message_content", "model_name", "model_params", "created_at")
    search_fields = ("chat_uuid", "user", "message_content")
    list_filter = ("message_type", "model_name")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
