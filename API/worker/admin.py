from django.contrib import admin

from import_export.admin import ImportExportModelAdmin
from worker.models import Task


@admin.register(Task)
class TaskAdmin(ImportExportModelAdmin):
    list_display = ("user", "name", "work_type", "result_status", "created_at", "updated_at")
    search_fields = ("user__email", "name", "work_type", "result_status")
    list_filter = ("work_type", "result_status")
