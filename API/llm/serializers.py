from rest_framework import serializers


class LLMRequestSerializer(serializers.Serializer):
    model_name = serializers.CharField(required=True)
    prompt = serializers.CharField(required=True)
