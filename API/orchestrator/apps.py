from django.apps import AppConfig


class WorkerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orchestrator"

    def ready(self):
        # Import signals
        import orchestrator.chain.emotion_detection
        import orchestrator.chain.speech_2_text
        import orchestrator.chain.task_finished
