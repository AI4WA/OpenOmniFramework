from rest_framework import serializers


class TaskLLMRequestSerializer(serializers.Serializer):
    model_name = serializers.CharField(required=True,
                                       help_text="The model name to use for chat completion, "
                                                 "it can be found in the llm_config_list endpoint")
    prompt = serializers.CharField(required=True, help_text="The prompt to use for chat completion")
    llm_task_type = serializers.ChoiceField(required=True,
                                            help_text="The type of task to run, it can be either llm or stt",
                                            choices=[
                                                ("chat_completion", "Chat Completion"),
                                                ("completion", "Completion"),
                                                ("create_embedding", "Create Embedding")
                                            ],
                                            )


class TaskLLMRequestsSerializer(serializers.Serializer):
    model_name = serializers.CharField(required=True,
                                       help_text="The model name to use for chat completion, "
                                                 "it can be found in the llm_config_list endpoint")
    prompts = serializers.ListField(child=serializers.CharField(), required=True,
                                    help_text="The prompts to use for chat completion")
    llm_task_type = serializers.ChoiceField(required=True,
                                            help_text="The type of task to run, it can be either llm or stt",
                                            choices=[
                                                ("chat_completion", "Chat Completion"),
                                                ("completion", "Completion"),
                                                ("create_embedding", "Create Embedding")
                                            ],
                                            )


class TaskSTTRequestSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True, help_text="The uid of the audio file to transcribe")
    audio_index = serializers.CharField(required=True, help_text="The index of the audio file to transcribe")
    start_time = serializers.DateTimeField(required=True, help_text="The start time of the audio file to transcribe")
    end_time = serializers.DateTimeField(required=True, help_text="The end time ofthe audio file to transcribe")
    hardware_device_mac_address = serializers.CharField(required=False,
                                                        help_text="The mac address of the hardware device",
                                                        )
