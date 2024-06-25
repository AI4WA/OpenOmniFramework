from rest_framework import serializers

from orchestrator.models import Task, TaskWorker


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class TaskWorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskWorker
        fields = "__all__"
