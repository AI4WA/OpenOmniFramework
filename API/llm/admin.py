from django.contrib import admin
# Register your models here.
from import_export.admin import ImportExportModelAdmin

from llm.models import LLMRequestRecord, LLMConfigRecords


@admin.register(LLMRequestRecord)
class LLMRequestRecordAdmin(ImportExportModelAdmin):
    list_display = ("user", "model_name", "task", "created_at", "updated_at")
    search_fields = ("user__username", "model_name", "task")
    list_filter = ("user", "model_name", "task")


@admin.register(LLMConfigRecords)
class LLMConfigRecordsAdmin(ImportExportModelAdmin):
    list_display = ("model_name", "model_size", "model_family", "model_type", "available", "created_at", "updated_at")
    search_fields = ("model_name", "model_size", "model_family", "model_type")
    list_filter = ("model_name", "model_size", "model_family", "model_type", "available")
