from django import forms
from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from import_export.admin import ImportExportModelAdmin

from orchestrator.metrics.benchmark import Benchmark
from orchestrator.models import Task, TaskWorker


class TaskAdminForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = "__all__"

    task_name = forms.ChoiceField(choices=Task.get_task_name_choices())


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    change_list_template = "admin/orchestrator/task/change_list.html"

    # get task_name to be the choices field
    form = TaskAdminForm
    list_display = (
        "id",
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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "benchmark/",
                self.admin_site.admin_view(self.benchmark),
                name="benchmark",
            ),
            path(
                "benchmark_detail/",
                self.admin_site.admin_view(self.benchmark_detail),
                name="benchmark_detail",
            ),
        ]
        return custom_urls + urls

    @staticmethod
    def benchmark(request):
        benchmark = Benchmark(benchmark_cluster="all")
        html_content = benchmark.run()
        context = {"content": html_content, "benchmark_type": "Latency Overall"}
        return render(request, "admin/orchestrator/task/benchmark.html", context)

    @staticmethod
    def benchmark_detail(request):
        benchmark = Benchmark(benchmark_cluster="all")
        html_content = benchmark.run_detail()
        context = {"content": html_content, "benchmark_type": "Latency Details"}
        return render(request, "admin/orchestrator/task/benchmark.html", context)


@admin.register(TaskWorker)
class TaskWorkerAdmin(ImportExportModelAdmin):
    list_display = ("uuid", "created_at", "updated_at")
    search_fields = ("uuid",)
    readonly_fields = ("created_at", "updated_at")
