# model types
HF_LLAMA = "HuggingFace"
MT_LLAMA = "llama.cpp"
MT_API = "api"
MT_CHATGLM = "chatglm.cpp"
MODEL_TYPES = [MT_LLAMA, MT_API, MT_CHATGLM]

# model names
MN_LLAMA2 = "llama2"
HF_LLAMA2 = "llama2-hf"
HF_LLAMA3 = "llama3-hf"
MN_GEMMA = "gemma"

MODELS = [
    {
        "name": MN_LLAMA2,
        "model_type": MT_LLAMA,
        "models": [
            {
                "name": "llama2-7b",
                "size": "7b",
                "repo": "TheBloke/Llama-2-7B-GGUF",
                "filename": "llama-2-7b.Q4_K_M.gguf",
            },
            {
                "name": "llama2-7b-chat",
                "size": "7b",
                "repo": "TheBloke/Llama-2-7B-Chat-GGUF",
                "filename": "llama-2-7b-chat.Q4_K_M.gguf",
            },
            {
                "name": "llama2-13b",
                "size": "13b",
                "repo": "TheBloke/Llama-2-13B-GGUF",
                "filename": "llama-2-13b.Q4_K_M.gguf",
            },
            {
                "name": "llama2-13b-chat",
                "size": "13b",
                "repo": "TheBloke/Llama-2-13B-Chat-GGUF",
                "filename": "llama-2-13b-chat.Q8_0.gguf",
            },
        ],
    },
    {
        "name": MN_GEMMA,
        "model_type": MT_LLAMA,
        "models": [
            {
                "name": "gemma-2b",
                "size": "2b",
                "repo": "brittlewis12/gemma-2b-GGUF",
                "filename": "gemma-2b.Q4_K_M.gguf",
            },
            {
                "name": "gemma-2b-instruct",
                "size": "2b",
                "repo": "brittlewis12/gemma-2b-it-GGUF",
                "filename": "gemma-2b-it.Q4_K_M.gguf",
            },
            {
                "name": "gemma-7b",
                "repo": "brittlewis12/gemma-7b-GGUF",
                "size": "7b",
                "filename": "gemma-7b.Q4_K_M.gguf",
            },
            {
                "name": "gemma-7b-instruct",
                "repo": "brittlewis12/gemma-7b-it-GGUF",
                "size": "7b",
                "filename": "gemma-7b-it.Q4_K_M.gguf",
            },
        ],
    },
    {
        "name": "internlm",
        "model_type": MT_LLAMA,
        "models": [
            {
                "name": "internlm-20b",
                "size": "20b",
                "repo": "intervitens/internlm-chat-20b-GGUF",
                "filename": "internlm-chat-20b.Q4_K_M.gguf",
            },
        ],
    },
    {
        "name": "chatglm",
        "model_type": MT_CHATGLM,
        "models": [
            {
                "name": "chatglm3-6b",
                "size": "6b",
                "repo": "npc0/chatglm3-6b-int4",
                "filename": "chatglm3-ggml-q4_1.bin",
            }
        ],
    },
    {
        "name": "dolphin-2.5-mixtral",
        "model_type": MT_LLAMA,
        "models": [
            {
                "name": "dolphin-2.5-mixtral-7x7b",
                "size": "8x7b",
                "repo": "TheBloke/dolphin-2.5-mixtral-8x7b-GGUF",
                "filename": "dolphin-2.5-mixtral-8x7b.Q2_K.gguf",
            }
        ],
    },
    {
        "name": "medicine-llm",
        "model_type": MT_LLAMA,
        "models": [
            {
                "name": "medicine-llm-13b",
                "size": "13b",
                "repo": "TheBloke/medicine-LLM-13B-GGUF",
                "filename": "medicine-llm-13b.Q8_0.gguf",
            }
        ],
    },
    {
        "name": "medicine-chat",
        "model_type": MT_LLAMA,
        "models": [
            {
                "name": "medicine-chat",
                "size": "13b",
                "repo": "TheBloke/medicine-chat-GGUF",
                "filename": "medicine-chat.Q8_0.gguf",
            }
        ],
    },
    {
        "name": "SOLAR-10",
        "model_type": MT_LLAMA,
        "models": [
            {
                "name": "SOLAR-10",
                "size": "7b",
                "repo": "TheBloke/SOLAR-10.7B-Instruct-v1.0-GGUF",
                "filename": "solar-10.7b-instruct-v1.0.Q8_0.gguf",
            }
        ],
    },
    {
        "name": "Mixtral-8x7b",
        "model_type": MT_LLAMA,
        "models": [
            {
                "name": "Mixtral-8x7b",
                "size": "8x7b",
                "repo": "TheBloke/Mixtral-8x7B-v0.1-GGUF",
                "filename": "mixtral-8x7b-v0.1.Q5_K_M.gguf",
            }
        ],
    },
    {
        "name": HF_LLAMA2,
        "model_type": HF_LLAMA,
        "models": [
            {
                "name": "Llama-2-7b-hf",
                "size": "7b",
                "repo":"",
                "filename":""
            },
            {
                "name": "Llama-2-7b-chat-hf",
                "size": "7b",
                "repo": "",
                "filename": ""
            },
            {
                "name": "Llama-2-13b-hf",
                "size": "13b",
                "repo": "",
                "filename": ""
            },
            {
                "name": "Llama-2-13b-chat-hf",
                "size": "13b",
                "repo": "",
                "filename": ""
            }
        ]
    },
    {
        "name": HF_LLAMA3,
        "model_type": HF_LLAMA,
        "models": [
            {
                "name": "Meta-Llama-3-8B",
                "size": "8b",
                "repo": "",
                "filename": ""
            },
            {
            "name": "Meta-Llama-3-8B-Instruct",
            "size": "8b",
                "repo": "",
                "filename": ""
            },
        ]
    },
]
