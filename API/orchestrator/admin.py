from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from orchestrator.models import Task, TaskWorker


@admin.register(Task)
class TaskAdmin(ImportExportModelAdmin):
    list_display = (
        "user",
        "name",
        "task_name",
        "process_delay_seconds",
        "result_status",
        "created_at",
        "updated_at",
    )
    search_fields = ("user__email", "name", "task_name", "result_status")
    list_filter = ("task_name", "result_status", "user")

    @admin.display(description="process_delay")
    def process_delay_seconds(self, obj):
        """
        The delay time of the task in seconds
        """
        if obj.updated_at is None:
            return 0
        return (obj.updated_at - obj.created_at).total_seconds()

    readonly_fields = ("created_at", "updated_at", "process_delay_seconds")


@admin.register(TaskWorker)
class TaskWorkerAdmin(ImportExportModelAdmin):
    list_display = ("uuid", "created_at", "updated_at")
    search_fields = ("uuid",)
    readonly_fields = ("created_at", "updated_at")
