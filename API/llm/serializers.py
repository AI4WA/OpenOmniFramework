from rest_framework import serializers

from llm.models import LLMConfigRecords


class LLMRequestSerializer(serializers.Serializer):
    model_name = serializers.CharField(
        required=True,
        help_text="The model name to use for chat completion, "
        "it can be found in the llm_config_list endpoint",
    )
    prompt = serializers.CharField(
        required=True, help_text="The prompt to use for chat completion"
    )


class LLMCustomRequestSerializer(LLMRequestSerializer):
    prompt = serializers.JSONField(
        required=True,
        help_text="The custom prompt needs to specify the roles for both the system and the user, "
        "along with their respective prompts, in JSON format for chat completion.",
    )


class LLMResponseSerializer(serializers.Serializer):
    response = serializers.JSONField(
        help_text="The response from the model, normally a JSON object. "
        "For all models with llama.cpp backend, the response is a string."
        "The response is the same, but for other models, "
        "the response will be different"
    )


class LLMConfigRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LLMConfigRecords
        fields = "__all__"
