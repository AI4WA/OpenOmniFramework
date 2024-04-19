from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LLM_MODEL_DIR = BASE_DIR / "llm" / "models"

API_DOMAIN = "https://api.nlp-tlp.org"

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
