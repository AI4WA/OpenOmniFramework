from rest_framework import serializers

from llm.models import LLMConfigRecords


class LLMConfigRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LLMConfigRecords
        fields = "__all__"
