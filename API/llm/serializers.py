from rest_framework import serializers
from llm.models import LLMConfigRecords


class LLMRequestSerializer(serializers.Serializer):
    model_name = serializers.CharField(required=True)
    prompt = serializers.CharField(required=True)


class LLMConfigRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LLMConfigRecords
        fields = "__all__"
