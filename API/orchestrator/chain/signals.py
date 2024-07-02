from django.dispatch import Signal

completed_task = Signal()  # task itself
completed_speech2text = Signal()  # task type
completed_emotion_detection = Signal()  # task type
completed_quantization_llm = Signal()  # task type
completed_hf_llm = Signal()  # task type
completed_text2speech = Signal()  # task type
completed_openai_speech2text = Signal()  # task type
completed_openai_gpt_4o_text_and_image = Signal()  # task type
completed_openai_gpt_4o_text_only = Signal()  # task type
created_data_text = Signal()
