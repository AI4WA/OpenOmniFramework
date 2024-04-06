from datetime import datetime

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.helpers import ActionForm
from import_export import resources

# Register your models here.
from import_export.admin import ImportExportModelAdmin

from authenticate.utils.fire_and_forget import fire_and_forget
from llm.models import LLMConfigRecords, LLMRequestRecord, LLMRequestResultDownload


class LLMRequestRecordResource(resources.ModelResource):
    class Meta:
        model = LLMRequestRecord


class TaskNameActionForm(ActionForm):
    task_name = forms.CharField(label="Task Name", required=False)


@admin.action(description="Export to CSV file")
@fire_and_forget
def export_to_csv(modeladmin, request, queryset):
    task_name = request.POST.get("task_name", None)
    if task_name is None:
        messages.add_message(request, messages.ERROR, "Task Name is required")
        return
    resource = LLMRequestRecordResource()
    dataset = resource.export(
        queryset=LLMRequestRecord.objects.filter(name=task_name, success=True)
    )
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(
        f"{settings.TMP_FOLDER}/{task_name}_{current_datetime}.csv", "wb"
    ) as file:
        file.write(dataset.csv.encode())


@admin.register(LLMRequestRecord)
class LLMRequestRecordAdmin(ImportExportModelAdmin):
    list_display = (
        "user",
        "model_name",
        "name",
        "task",
        "success",
        "completed_in_seconds",
        "updated_at",
    )
    search_fields = (
        "user__username",
        "model_name",
        "task",
        "name",
    )
    list_filter = (
        "user",
        "name",
        "model_name",
        "task",
        "success",
        "user__organization",
    )
    action_form = TaskNameActionForm
    actions = [export_to_csv]


@admin.register(LLMConfigRecords)
class LLMConfigRecordsAdmin(ImportExportModelAdmin):
    list_display = (
        "model_name",
        "model_size",
        "model_family",
        "model_type",
        "available",
        "created_at",
        "updated_at",
    )
    search_fields = ("model_name", "model_size", "model_family", "model_type")
    list_filter = (
        "model_name",
        "model_size",
        "model_family",
        "model_type",
        "available",
    )


@admin.register(LLMRequestResultDownload)
class LLMRequestResultDownloadAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "progress",
        "download_link",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "user",
        "progress",
    )
    search_fields = ("name",)
