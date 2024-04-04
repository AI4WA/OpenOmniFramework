from rest_framework import serializers

from worker.models import Task, TaskWorker


class TaskLLMRequestSerializer(serializers.Serializer):
    task_type = serializers.ChoiceField(
        help_text="The worker to assign the task to",
        choices=[
            ("cpu", "cpu"),
            ("gpu", "GPU"),
        ],
        default="cpu",
    )
    name = serializers.CharField(
        required=False,
        help_text="The name of the task to run, which can help you track a list of tasks",
        default="default_name",
    )
    model_name = serializers.CharField(
        required=True,
        help_text="The model name to use for chat completion, "
        "it can be found in the llm_config_list endpoint",
    )
    prompt = serializers.CharField(
        required=True, help_text="The prompt to use for chat completion"
    )
    llm_task_type = serializers.ChoiceField(
        required=True,
        help_text="The type of task to run, it can be either llm or stt",
        choices=[
            ("chat_completion", "Chat Completion"),
            ("completion", "Completion"),
            ("create_embedding", "Create Embedding"),
        ],
    )


# custom a serializer field to handle the prompt
class LiteralChoiceField(serializers.ChoiceField):
    def __init__(self, choices, **kwargs):
        # In DRF, choices are expected to be a list of tuples (value, human-readable name),
        # but for a Literal field, you can simplify this by providing the choices directly.
        super().__init__(choices=[(choice, choice) for choice in choices], **kwargs)


class ChatCompletionRequestMessageSerializer(serializers.Serializer):
    role = LiteralChoiceField(
        choices=["system", "user", "assistant", "function"],
        default="user",
        help_text="The role of the message.",
    )
    # Add the content field
    content = serializers.CharField(
        allow_blank=True, default="", help_text="The content of the message."
    )


class ChatCompletionFunctionSerializer(serializers.Serializer):
    name = serializers.CharField(
        required=True,
        help_text="The name of the function to call",
    )
    description = serializers.CharField(
        required=False,
        help_text="The description of the function",
    )
    parameters = serializers.JSONField(
        required=False,
        help_text="""The parameters of the function
                  Example:
                  {
                      "type": "object",
                      "properties": {
                          "loc_origin": {
                              "type": "string",
                              "description": "The departure airport, e.g. DUS"
                          },
                          "loc_destination": {
                              "type": "string",
                              "description": "The destination airport, e.g. HAM"
                          }
                      },
                  "required": ["loc_origin", "loc_destination"]
                  }
                  """,
    )


class TaskCustomLLMRequestSerializer(serializers.Serializer):
    task_type = serializers.ChoiceField(
        help_text="The worker to assign the task to",
        choices=[
            ("cpu", "cpu"),
            ("gpu", "GPU"),
        ],
        default="cpu",
    )
    name = serializers.CharField(
        required=False,
        help_text="The name of the task to run, which can help you track a list of tasks",
        default="default_name",
    )
    model_name = serializers.CharField(
        required=True,
        help_text="The model name to use for chat completion, "
        "it can be found in the llm_config_list endpoint",
    )
    llm_task_type = serializers.ChoiceField(
        required=True,
        help_text="The type of task to run, it can be either llm or stt",
        choices=[
            ("chat_completion", "Chat Completion"),
            ("completion", "Completion"),
            ("create_embedding", "Create Embedding"),
        ],
    )
    # message is a list of ChatCompletionRequestMessageSerializer
    messages = serializers.ListField(
        child=ChatCompletionRequestMessageSerializer(),
        required=False,
        help_text="The messages to use for chat completion",
    )
    functions = serializers.ListField(
        child=ChatCompletionFunctionSerializer(),
        required=False,
        help_text="The functions to use for chat completion",
    )
    function_call = serializers.CharField(
        required=False,
        help_text="The function call to use for chat completion, can be none or auto, "
        "or a function you mentioned in functions",
        default="auto",
    )


class TaskLLMRequestsSerializer(serializers.Serializer):
    task_type = serializers.ChoiceField(
        help_text="The worker to assign the task to",
        choices=[
            ("cpu", "cpu"),
            ("gpu", "GPU"),
        ],
        default="cpu",
    )
    name = serializers.CharField(
        required=False,
        help_text="The name of the task to run, which can help you track a list of tasks",
        default="default_name",
    )
    model_name = serializers.CharField(
        required=True,
        help_text="The model name to use for chat completion, "
        "it can be found in the llm_config_list endpoint",
    )
    prompts = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        help_text="The prompts to use for chat completion",
    )
    llm_task_type = serializers.ChoiceField(
        required=True,
        help_text="The type of task to run, it can be either llm or stt",
        choices=[
            ("chat_completion", "Chat Completion"),
            ("completion", "Completion"),
            ("create_embedding", "Create Embedding"),
        ],
    )


class TaskSTTRequestSerializer(serializers.Serializer):
    uid = serializers.CharField(
        required=True, help_text="The uid of the audio file to transcribe"
    )
    audio_index = serializers.CharField(
        required=True, help_text="The index of the audio file to transcribe"
    )
    start_time = serializers.DateTimeField(
        required=True, help_text="The start time of the audio file to transcribe"
    )
    end_time = serializers.DateTimeField(
        required=True, help_text="The end time ofthe audio file to transcribe"
    )
    hardware_device_mac_address = serializers.CharField(
        required=False,
        help_text="The mac address of the hardware device",
    )


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
