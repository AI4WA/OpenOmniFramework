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

CLUSTER_ETE_CONVERSATION_NAME = "CLUSTER_ETE_CONVERSATION"

CLUSTER_ETE_CONVERSATION = {
    "completed_speech2text": {
        "order": 1,
        "extra_params": {},
    },
    "created_data_text": {
        "order": 2,
        "extra_params": {},
    },
    "completed_emotion_detection": {
        "order": 3,
        "extra_params": {},
    },
    "completed_quantization_llm": {
        "order": 4,
        "extra_params": {
            "llm_model_name": "SOLAR-10",
        },
    },
    "completed_text2speech": {
        "order": 5,
        "extra_params": {},
    },
}

CLUSTERS = {
    CLUSTER_ETE_CONVERSATION_NAME: CLUSTER_ETE_CONVERSATION,
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
