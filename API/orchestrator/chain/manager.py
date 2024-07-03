"""

Here will define a list of clusters

Each cluster will have a list of chain components

For example, end-to-end conversation chain will have the following components:

- completed_speech2text
- created_data_text
- completed_emotion_detection
- completed_quantization_llm
- completed_text2speech
"""

from typing import Optional, Tuple

from authenticate.utils.get_logger import get_logger
from orchestrator.chain.signals import created_data_text
from orchestrator.models import Task

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
            "hf_model_name": "stabilityai/stablelm-3b-4e1t",
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

CLUSTERS = {
    CLUSTER_Q_ETE_CONVERSATION_NAME: CLUSTER_Q_ETE_CONVERSATION,
    CLUSTER_HF_ETE_CONVERSATION_NAME: CLUSTER_HF_ETE_CONVERSATION,
    CLUSTER_GPT_4O_ETE_CONVERSATION_NAME: CLUSTER_GPT_4O_ETE_CONVERSATION,
    CLUSTER_GPT_4O_TEXT_ETE_CONVERSATION_NAME: CLUSTER_GPT_4O_TEXT_ETE_CONVERSATION,
    CLUSTER_Q_NO_EMOTION_ETE_CONVERSATION_NAME: CLUSTER_Q_NO_EMOTION_ETE_CONVERSATION,
}


class ClusterManager:

    @staticmethod
    def get_cluster(cluster_name: str):
        """
        Get the cluster

        Args:
            cluster_name (str): The cluster name
        """
        if cluster_name in CLUSTERS:
            return CLUSTERS[cluster_name]
        return None

    @staticmethod
    def get_next_chain_component(
        cluster: dict, current_component: str
    ) -> Tuple[Optional[str], Optional[dict]]:
        """
        Get the next chain

        Args:
            cluster (dict): The cluster
            current_component (str): The current component

        Return:
            Tuple[Optional[str], Optional[dict]]: The next component and its parameters if exists, otherwise None
        """
        chain = []
        for key, value in cluster.items():
            chain.append(key)
        chain.sort(key=lambda x: cluster[x]["order"])
        if current_component == "init":
            """
            If this is the start of the chain, then return the first component
            """
            return chain[0], cluster[chain[0]]
        # index of the current component
        current_component_index = chain.index(current_component)
        next_index = current_component_index + 1
        if next_index >= len(chain):
            return None, None
        return chain[next_index], cluster[chain[next_index]]

    @classmethod
    def get_next(cls, cluster_name: str, current_component: str):
        """
        Get the next component

        Args:
            cluster_name (str): The cluster name
            current_component (str): The current component
        """
        cluster = cls.get_cluster(cluster_name)
        if cluster is None:
            return None
        return ClusterManager.get_next_chain_component(cluster, current_component)

    @classmethod
    def chain_next(
        cls,
        track_id: Optional[str],
        current_component: str,
        next_component_params: dict,
        name: str = None,
        user=None,
    ):
        """
        Chain to the next component

        Args:
            current_component (str): The current component
            track_id (str): The track ID
            next_component_params (dict): The next component parameters
            name (str): The task name, it will be used to aggregate the task
            user (None): The user
        """
        logger.info(f"Current component: {current_component}")
        logger.info(f"Next component params: {next_component_params}")
        cluster_name = track_id.split("-")[1]
        next_component_name, next_component = cls.get_next(
            cluster_name, current_component
        )
        logger.info(f"Next component: {next_component_name}")

        if next_component_name is None:
            return
        # do something with the next component
        # It can be a task or a signal
        next_parameters = {
            **next_component_params,
            **next_component.get("extra_params", {}),
        }
        logger.info(next_parameters)
        logger.info(next_component_name)

        if next_component["component_type"] == "task":
            task = Task.create_task(
                user=user,
                name=name or next_component["task_name"],
                task_name=next_component["task_name"],
                parameters=next_parameters,
                track_id=track_id,
            )
            logger.info(f"Task {task.id} created for {next_component['task_name']}")
            return task.id
        elif next_component["component_type"] == "signal":
            if next_component_name == "created_data_text":
                created_data_text.send(
                    sender=next_component_params.get("sender"),
                    data=next_component_params.get("data"),
                    track_id=track_id,
                    user=user,
                )
        return None
