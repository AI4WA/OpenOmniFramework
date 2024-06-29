from django import forms
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from orchestrator.metrics.benchmark import Benchmark
from orchestrator.models import Task, TaskWorker


class TaskAdminForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = "__all__"

    task_name = forms.ChoiceField(choices=Task.get_task_name_choices())


@admin.action(description="Run Benchmark")
def run_benchmark(modeladmin, request, queryset):
    benchmark = Benchmark(benchmark_cluster="all")
    benchmark.run()


@admin.register(Task)
class TaskAdmin(ImportExportModelAdmin):
    # get task_name to be the choices field
    form = TaskAdminForm
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
    actions = [run_benchmark]


@admin.register(TaskWorker)
class TaskWorkerAdmin(ImportExportModelAdmin):
    list_display = ("uuid", "created_at", "updated_at")
    search_fields = ("uuid",)
    readonly_fields = ("created_at", "updated_at")
