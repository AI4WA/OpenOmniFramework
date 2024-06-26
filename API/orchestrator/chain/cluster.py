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

from orchestrator.models import Task
from typing import Optional, Tuple
from orchestrator.chain.signals import created_data_text

CLUSTER_Q_ETE_CONVERSATION_NAME = "CLUSTER_Q_ETE_CONVERSATION"

CLUSTER_Q_ETE_CONVERSATION = {
    "completed_speech2text": {"order": 1, "extra_params": {}, "component_type": "task"},
    "created_data_text": {"order": 2, "extra_params": {}, "component_type": "signal"},
    "completed_emotion_detection": {
        "order": 3,
        "extra_params": {},
        "component_type": "task",
    },
    "completed_quantization_llm": {
        "order": 4,
        "extra_params": {
            "llm_model_name": "SOLAR-10",
        },
        "component_type": "task",
    },
    "completed_text2speech": {"order": 5, "extra_params": {}, "component_type": "task"},
}

CLUSTER_HF_ETE_CONVERSATION_NAME = "CLUSTER_HF_ETE_CONVERSATION"

CLUSTER_HF_ETE_CONVERSATION = {
    "completed_speech2text": {"order": 1, "extra_params": {}, "component_type": "task"},
    "created_data_text": {"order": 2, "extra_params": {}, "component_type": "signal"},
    "completed_emotion_detection": {
        "order": 3,
        "extra_params": {},
        "component_type": "task",
    },
    "completed_hf_llm": {
        "order": 4,
        "extra_params": {
            "hf_model_name": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        },
        "component_type": "task",
    },
    "completed_text2speech": {"order": 5, "extra_params": {}, "component_type": "task"},
}

CLUSTERS = {
    CLUSTER_Q_ETE_CONVERSATION_NAME: CLUSTER_Q_ETE_CONVERSATION,
    CLUSTER_HF_ETE_CONVERSATION_NAME: CLUSTER_HF_ETE_CONVERSATION,
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
    ):
        """
        Chain to the next component

        Args:
            current_component (str): The current component
            track_id (str): The track ID
            next_component_params (dict): The next component parameters
        """
        cluster_name = track_id.split("-")[1]
        next_component_name, next_component = cls.get_next(
            cluster_name, current_component
        )
        if next_component_name is None:
            return
        # do something with the next component
        # It can be a task or a signal
        next_parameters = {
            **next_component_params,
            **next_component.get("extra_params", {}),
        }

        task_mapping = {
            "completed_quantization_llm": "quantization_llm",
            "completed_hf_llm": "hf_llm",
            "completed_text2speech": "text2speech",
            "completed_emotion_detection": "emotion_detection",
        }

        if next_component_name in task_mapping:
            Task.create_task(
                user=None,
                name=task_mapping[next_component_name],
                task_name=task_mapping[next_component_name],
                parameters=next_parameters,
                track_id=track_id,
            )
        elif next_component_name == "created_data_text":
            created_data_text.send(
                sender=next_component_params.get("sender"),
                data=next_component_params.get("data"),
                track_id=track_id,
            )
