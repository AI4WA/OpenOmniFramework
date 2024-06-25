from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from orchestrator.models import Task, TaskWorker


@admin.register(Task)
class TaskAdmin(ImportExportModelAdmin):
    list_display = (
        "user",
        "name",
        "task_name",
        "result_status",
        "created_at",
        "updated_at",
    )
    search_fields = ("user__email", "name", "task_name", "result_status")
    list_filter = ("task_name", "result_status", "user")

    readonly_fields = ("created_at", "updated_at")


@admin.register(TaskWorker)
class TaskWorkerAdmin(ImportExportModelAdmin):
    list_display = ("uuid", "created_at", "updated_at")
    search_fields = ("uuid",)
    readonly_fields = ("created_at", "updated_at")
