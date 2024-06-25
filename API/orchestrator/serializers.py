from rest_framework import serializers

from orchestrator.models import Task, TaskWorker


class TaskRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class TaskReportSerializer(serializers.Serializer):
    result_status = serializers.ChoiceField(
        help_text="The status of the result",
        choices=[
            ("completed", "completed"),
            ("failed", "Failed"),
        ],
        default="completed",
    )
    description = serializers.CharField(
        required=False, help_text="The description of the result"
    )
    result = serializers.JSONField(required=False, help_text="The result of the task")
    completed_in_seconds = serializers.FloatField(
        required=False, help_text="The time taken to complete the task"
    )
    success = serializers.BooleanField(
        required=False, help_text="The success status of the task"
    )


class TaskWorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskWorker
        fields = "__all__"
