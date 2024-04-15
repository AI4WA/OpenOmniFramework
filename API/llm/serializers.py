from rest_framework import serializers

from llm.models import LLMConfigRecords


class LLMConfigRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LLMConfigRecords
        fields = "__all__"


class LLMRequestResultDownloadSerializer(serializers.Serializer):
    task_name = serializers.CharField(
        required=True,
        help_text="The task name to download the result",
    )
