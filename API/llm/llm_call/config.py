# model types
MT_LLAMA = "llama.cpp"
MT_API = "api"
MT_CHATGLM = "chatglm.cpp"
MODEL_TYPES = [MT_LLAMA, MT_API, MT_CHATGLM]

# model names
MN_LLAMA2 = "llama2"
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
            }
        ]
    },
    {
        "name": MN_GEMMA,
        "model_type": MT_LLAMA,
        "models": [
            {
                "name": "gemma-2b",
                "size": "2b",
                "repo": "brittlewis12/gemma-2b-GGUF",
                "filename": "gemma-2b.Q4_K_M.gguf"
            },
            {
                "name": "gemma-2b-instruct",
                "size": "2b",
                "repo": "brittlewis12/gemma-2b-it-GGUF",
                "filename": "gemma-2b-it.Q4_K_M.gguf"
            },
            {
                "name": "gemma-7b",
                "repo": "brittlewis12/gemma-7b-GGUF",
                "size": "7b",
                "filename": "gemma-7b.Q4_K_M.gguf"
            },
            {
                "name": "gemma-7b-instruct",
                "repo": "brittlewis12/gemma-7b-it-GGUF",
                "size": "7b",
                "filename": "gemma-7b-it.Q4_K_M.gguf"
            }
        ]
    },
    {
        "name": "chatglm",
        "model_type": MT_CHATGLM,
        "models": [
            {
                "name": "chatglm3-6b",
                "size": "6b",
                "repo": "npc0/chatglm3-6b-int4",
                "filename": "chatglm3-ggml-q4_1.bin"
            }
        ]
    }
]
