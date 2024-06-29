# Cluster

We use the Django **Signal** and the **orchestrator.chain.cluster** to manage the pipelines.

You can pre-define a cluster within the `orchestrator.chain.cluster` module.

We have several predefined ones there

```python
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
```

This is one for a standard end-to-end conversation pipeline.
We use the quantization model `SOLAR-10` to generate the response.