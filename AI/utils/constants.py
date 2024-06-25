from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LLM_MODEL_DIR = BASE_DIR / "llm" / "models"
EMOTION_DETECTION_MODEL_DIR = BASE_DIR / "emotion_detection" / "models"

DATA_DIR = BASE_DIR.parent / "data"

DATA_DIR.mkdir(exist_ok=True)

API_DOMAIN = "http://localhost:8000"  # default domain

# model types
HF_LLAMA = "HuggingFace"
MT_LLAMA = "llama.cpp"
MT_API = "api"
MT_CHATGLM = "chatglm.cpp"
MODEL_TYPES = [HF_LLAMA, MT_LLAMA, MT_API, MT_CHATGLM]

# model names
MN_LLAMA2 = "llama2"
MN_GEMMA = "gemma"

BERT = "bert"
NORMAL_MODELS = [BERT]


"""
```python3
LLM_MODEL_DIR = BASE_DIR / "llm" / "models"

API_DOMAIN = "http://localhost:8000"  # default domain

# model types
HF_LLAMA = "HuggingFace"
MT_LLAMA = "llama.cpp"
MT_API = "api"
MT_CHATGLM = "chatglm.cpp"
MODEL_TYPES = [HF_LLAMA, MT_LLAMA, MT_API, MT_CHATGLM]

# model names
MN_LLAMA2 = "llama2"
MN_GEMMA = "gemma"

BERT = "bert"
NORMAL_MODELS = [BERT]
```

"""


CLIENT_DATA_FOLDER = BASE_DIR.parent.parent / "Client" / "Listener" / "data"
