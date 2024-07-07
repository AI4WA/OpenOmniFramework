from authenticate.utils.get_logger import get_logger

logger = get_logger(__name__)

"""
This is for the quantization LLM model for the ETE conversation
"""
CLUSTER_Q_ETE_CONVERSATION_NAME = "CLUSTER_Q_ETE_CONVERSATION"

CLUSTER_Q_ETE_CONVERSATION = {
    "speech2text": {
        "order": 0,
        "extra_params": {},
        "component_type": "task",
        "task_name": "speech2text",
    },
    "completed_speech2text": {
        "order": 1,
        "extra_params": {},
        "component_type": "signal",
        "task_name": None,
    },
    "created_data_text": {
        "order": 2,
        "extra_params": {},
        "component_type": "signal",
        "task_name": None,
    },
    "completed_emotion_detection": {
        "order": 3,
        "extra_params": {},
        "component_type": "task",
        "task_name": "emotion_detection",
    },
    "completed_quantization_llm": {
        "order": 4,
        "extra_params": {
            "llm_model_name": "SOLAR-10",
        },
        "component_type": "task",
        "task_name": "quantization_llm",
    },
    "completed_text2speech": {
        "order": 5,
        "extra_params": {},
        "component_type": "task",
        "task_name": "text2speech",
    },
}
"""
Get rid of the emotion detection model
"""
CLUSTER_Q_NO_EMOTION_ETE_CONVERSATION_NAME = "CLUSTER_Q_NO_EMOTION_ETE_CONVERSATION"

CLUSTER_Q_NO_EMOTION_ETE_CONVERSATION = {
    "speech2text": {
        "order": 0,
        "extra_params": {},
        "component_type": "task",
        "task_name": "speech2text",
    },
    "completed_speech2text": {
        "order": 1,
        "extra_params": {},
        "component_type": "signal",
        "task_name": None,
    },
    "created_data_text": {
        "order": 2,
        "extra_params": {},
        "component_type": "signal",
        "task_name": None,
    },
    "completed_quantization_llm": {
        "order": 4,
        "extra_params": {
            "llm_model_name": "SOLAR-10",
        },
        "component_type": "task",
        "task_name": "quantization_llm",
    },
    "completed_text2speech": {
        "order": 5,
        "extra_params": {},
        "component_type": "task",
        "task_name": "text2speech",
    },
}

"""
This is the pipeline using the HF LLM model for the ETE conversation
"""

CLUSTER_HF_ETE_CONVERSATION_NAME = "CLUSTER_HF_ETE_CONVERSATION"

CLUSTER_HF_ETE_CONVERSATION = {
    "speech2text": {
        "order": 0,
        "extra_params": {},
        "component_type": "task",
        "task_name": "speech2text",
    },
    "completed_speech2text": {
        "order": 1,
        "extra_params": {},
        "component_type": "signal",
        "task_name": "None",
    },
    "created_data_text": {
        "order": 2,
        "extra_params": {},
        "component_type": "signal",
        "task_name": None,
    },
    "completed_emotion_detection": {
        "order": 3,
        "extra_params": {},
        "component_type": "task",
        "task_name": "emotion_detection",
    },
    "completed_hf_llm": {
        "order": 4,
        "extra_params": {
            "hf_model_name": "Qwen/Qwen2-7B-Instruct",
        },
        "component_type": "task",
        "task_name": "hf_llm",
    },
    "completed_text2speech": {
        "order": 5,
        "extra_params": {},
        "component_type": "task",
        "task_name": "text2speech",
    },
}

"""
Create one to use the full GPT-4o models.

In theory, it should takes the audio and video in, and then output audio.

However, until now, the API for audio is not yet available.

So we will use the walk around by using the speech to text model first, and then call GPT-4o
"""

CLUSTER_GPT_4O_ETE_CONVERSATION_NAME = "CLUSTER_GPT_4O_ETE_CONVERSATION"
CLUSTER_GPT_4O_ETE_CONVERSATION = {
    # first will call the openai model to convert the speech to text
    "openai_speech2text": {
        "order": 0,
        "extra_params": {},
        "component_type": "task",
        "task_name": "openai_speech2text",
    },
    "completed_openai_speech2text": {
        "order": 1,
        "extra_params": {},
        "component_type": "signal",
        "task_name": None,
    },
    "created_data_text": {
        "order": 2,
        "extra_params": {},
        "component_type": "signal",
        "task_name": None,
    },
    # then will call the GPT-4o model to convert the text to speech
    "completed_openai_gpt_4o_text_and_image": {
        "order": 2,
        "extra_params": {
            "sample_ratio": 10,
            "prompt_template": """
            You are a robot, and you are talking to a human.
            You will be provided with text and some flow of images, which actually are the video frames.

            Your task is to generate a response to the human based on the text and the images.

            You response will be directly send to end user.

            The text is: {text}
            """,
        },
        "component_type": "task",
        "task_name": "openai_gpt_4o_text_and_image",
    },
    # then the output should be directly the text, feed to speech 2 text
    "completed_openai_text2speech": {
        "order": 3,
        "extra_params": {},
        "component_type": "task",
        "task_name": "openai_text2speech",
    },
}

CLUSTER_GPT_4O_TEXT_ETE_CONVERSATION_NAME = "CLUSTER_GPT_4O_TEXT_ETE_CONVERSATION"
CLUSTER_GPT_4O_TEXT_ETE_CONVERSATION = {
    # first will call the openai model to convert the speech to text
    "openai_speech2text": {
        "order": 0,
        "extra_params": {},
        "component_type": "task",
        "task_name": "openai_speech2text",
    },
    "completed_openai_speech2text": {
        "order": 1,
        "extra_params": {},
        "component_type": "signal",
        "task_name": None,
    },
    # then will call the GPT-4o model to convert the text to speech
    "completed_openai_gpt_4o_text_only": {
        "order": 2,
        "extra_params": {
            "sample_ratio": 10,
            "prompt_template": """
            You are a robot, and you are talking to a human.

            Your task is to generate a response to the human based on the text

            You response will be directly send to end user.

            The text is: {text}
            """,
        },
        "component_type": "task",
        "task_name": "openai_gpt_4o_text_only",
    },
    # then the output should be directly the text, feed to speech 2 text
    "completed_openai_text2speech": {
        "order": 3,
        "extra_params": {},
        "component_type": "task",
        "task_name": "openai_text2speech",
    },
}


"""
Cluster for gpt3.5 model and gpt3.5 with RAG
"""
CLUSTER_GPT_35_ETE_CONVERSATION_NAME = "CLUSTER_GPT_35_ETE_CONVERSATION"
CLUSTER_GPT_35_ETE_CONVERSATION = {
    "openai_speech2text": {
        "order": 0,
        "extra_params": {},
        "component_type": "task",
        "task_name": "openai_speech2text",
    },
    "completed_openai_speech2text": {
        "order": 1,
        "extra_params": {},
        "component_type": "signal",
        "task_name": None,
    },
    "created_data_text": {
        "order": 2,
        "extra_params": {},
        "component_type": "signal",
        "task_name": None,
    },
    "completed_openai_gpt_35": {
        "order": 3,
        "extra_params": {
            "sample_ratio": 10,
            "prompt_template": """{text}""",
        },
        "component_type": "task",
        "task_name": "openai_gpt_35",
    },
    "completed_openai_text2speech": {
        "order": 4,
        "extra_params": {},
        "component_type": "task",
        "task_name": "openai_text2speech",
    },
}


"""
Cluster for gpt3.5 model and gpt3.5 with RAG
"""
CLUSTER_GPT_35_RAG_ETE_CONVERSATION_NAME = "CLUSTER_GPT_35_RAG_ETE_CONVERSATION"
CLUSTER_GPT_35_RAG_ETE_CONVERSATION = {
    "openai_speech2text": {
        "order": 0,
        "extra_params": {},
        "component_type": "task",
        "task_name": "openai_speech2text",
    },
    "completed_openai_speech2text": {
        "order": 1,
        "extra_params": {},
        "component_type": "signal",
        "task_name": None,
    },
    "created_data_text": {
        "order": 2,
        "extra_params": {},
        "component_type": "signal",
        "task_name": None,
    },
    "completed_rag": {
        "order": 3,
        "extra_params": {},
        "component_type": "task",
        "task_name": "rag",
    },
    "completed_openai_gpt_35": {
        "order": 4,
        "extra_params": {
            "prompt_template": """{text}""",
        },
        "component_type": "task",
        "task_name": "openai_gpt_35",
    },
    "completed_openai_text2speech": {
        "order": 5,
        "extra_params": {},
        "component_type": "task",
        "task_name": "openai_text2speech",
    },
}


CLUSTERS = {
    CLUSTER_Q_ETE_CONVERSATION_NAME: CLUSTER_Q_ETE_CONVERSATION,
    CLUSTER_HF_ETE_CONVERSATION_NAME: CLUSTER_HF_ETE_CONVERSATION,
    CLUSTER_GPT_4O_ETE_CONVERSATION_NAME: CLUSTER_GPT_4O_ETE_CONVERSATION,
    CLUSTER_GPT_4O_TEXT_ETE_CONVERSATION_NAME: CLUSTER_GPT_4O_TEXT_ETE_CONVERSATION,
    CLUSTER_Q_NO_EMOTION_ETE_CONVERSATION_NAME: CLUSTER_Q_NO_EMOTION_ETE_CONVERSATION,
    CLUSTER_GPT_35_ETE_CONVERSATION_NAME: CLUSTER_GPT_35_ETE_CONVERSATION,
    CLUSTER_GPT_35_RAG_ETE_CONVERSATION_NAME: CLUSTER_GPT_35_RAG_ETE_CONVERSATION,
}
