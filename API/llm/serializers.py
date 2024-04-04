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
    llm_task_type = "chat_completion"
    prompt = serializers.JSONField(
        required=True,
        help_text="The custom prompt to use for chat completion. Now can input 3 parameters in JSON format:"
        "messages: [{}] (required), functions: [{}] (optional), function_call: auto/none/{} (optional)",
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
