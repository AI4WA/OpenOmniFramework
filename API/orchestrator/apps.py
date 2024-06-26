from django.apps import AppConfig


class WorkerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orchestrator"

    def ready(self):
        # Import signals
        import orchestrator.chain.completed_emotion_detection
        import orchestrator.chain.completed_quantization_llm
        import orchestrator.chain.completed_speech2text
        import orchestrator.chain.completed_task
        import orchestrator.chain.completed_text2speech
        import orchestrator.chain.created_data_text
        import orchestrator.chain.completed_hf_llm
