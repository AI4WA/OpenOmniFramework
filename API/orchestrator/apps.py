from django.apps import AppConfig


class WorkerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orchestrator"

    def ready(self):  # noqa
        # Import signals
        import orchestrator.chain.completed_emotion_detection  # noqa
        import orchestrator.chain.completed_hf_llm  # noqa
        import orchestrator.chain.completed_openai_gpt_4o_text_and_image  # noqa
        import orchestrator.chain.completed_openai_gpt_4o_text_only  # noqa
        import orchestrator.chain.completed_openai_gpt_35  # noqa
        import orchestrator.chain.completed_openai_speech2text  # noqa
        import orchestrator.chain.completed_openai_text2speech  # noqa
        import orchestrator.chain.completed_quantization_llm  # noqa
        import orchestrator.chain.completed_rag  # noqa
        import orchestrator.chain.completed_speech2text  # noqa
        import orchestrator.chain.completed_task  # noqa
        import orchestrator.chain.completed_text2speech  # noqa
        import orchestrator.chain.created_data_text  # noqa
