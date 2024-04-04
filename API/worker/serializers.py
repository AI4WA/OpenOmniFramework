from rest_framework import serializers

from worker.models import GPUWorker, Task


class TaskLLMRequestSerializer(serializers.Serializer):
    task_worker = serializers.ChoiceField(
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


class TaskCustomLLMRequestSerializer(TaskLLMRequestSerializer):
    prompt = serializers.JSONField(
        required=True, help_text="The custom prompt to use for chat completion"
    )


class TaskLLMRequestsSerializer(serializers.Serializer):
    task_worker = serializers.ChoiceField(
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


class GPUWorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPUWorker
        fields = "__all__"
