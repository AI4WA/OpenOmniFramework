from django import forms

# import messages
from django.contrib import admin, messages
from django.shortcuts import render
from django.urls import path
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin

from orchestrator.chain.manager import CLUSTERS, ClusterManager
from orchestrator.chain.signals import completed_task
from orchestrator.metrics.benchmark import Benchmark
from orchestrator.models import Task, TaskWorker


class ClusterFilter(admin.SimpleListFilter):
    title = _("Cluster")
    parameter_name = "cluster"

    def lookups(self, request, model_admin):
        return [(cluster, cluster) for cluster in CLUSTERS]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(track_id__startswith=f"T-{self.value()}")
        return queryset


class TaskAdminForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = "__all__"

    task_name = forms.ChoiceField(choices=Task.get_task_name_choices())


@admin.action(description="Trigger Downstream Task")
def trigger_downstream_task(modeladmin, request, queryset):
    for task in queryset:
        completed_task.send(sender=task, data=task.__dict__)
        messages.add_message(
            request,
            messages.INFO,
            f"Triggered downstream task for {task.track_id} with current component completed_{task.task_name}",
        )


@admin.action(description="Reprocess Task")
def reprocess_task(modeladmin, request, queryset):
    for task in queryset:
        task.result_status = "pending"
        task.save()
        messages.add_message(
            request,
            messages.INFO,
            f"Reprocessed task for {task.track_id} with current component {task.task_name}",
        )


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
    search_fields = ("user__email", "name", "task_name", "result_status", "track_id")
    list_filter = ("task_name", "result_status", "user", ClusterFilter)
    actions = [trigger_downstream_task, reprocess_task]

    readonly_fields = ("created_at", "updated_at")

    def get_urls(self):
        # the custom urls will be changed when ClusterFilter is changed, how can I implement it?
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
        # get parameter from request url
        cluster = request.GET.get("cluster", "all")
        benchmark = Benchmark(benchmark_cluster=cluster)
        html_content = benchmark.run()
        context = {"content": html_content, "benchmark_type": "Latency Overall"}
        return render(request, "admin/orchestrator/task/benchmark.html", context)

    @staticmethod
    def benchmark_detail(request):
        cluster = request.GET.get("cluster", "all")
        benchmark = Benchmark(benchmark_cluster=cluster)
        html_content = benchmark.run_detail()
        context = {"content": html_content, "benchmark_type": "Latency Details"}
        return render(request, "admin/orchestrator/task/benchmark.html", context)


@admin.register(TaskWorker)
class TaskWorkerAdmin(ImportExportModelAdmin):
    list_display = ("uuid", "created_at", "updated_at")
    search_fields = ("uuid",)
    readonly_fields = ("created_at", "updated_at")
