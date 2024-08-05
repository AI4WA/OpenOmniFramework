from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LLM_MODEL_DIR = BASE_DIR / "data" / "models" / "llm"
EMOTION_DETECTION_MODEL_DIR = BASE_DIR / "data" / "models" / "emotion_detection"

DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(exist_ok=True)
LLM_MODEL_DIR.mkdir(exist_ok=True, parents=True)
EMOTION_DETECTION_MODEL_DIR.mkdir(exist_ok=True, parents=True)

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

CLIENT_DATA_FOLDER = BASE_DIR.parent / "Client" / "Listener" / "data"
CLIENT_DATA_FOLDER.mkdir(exist_ok=True, parents=True)
S3_BUCKET = "openomni"
