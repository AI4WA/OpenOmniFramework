from sentence_transformers import SentenceTransformer

from constants import BERT, NORMAL_MODELS


class MLModelConfig:
    def __init__(self, model_name: str):
        if model_name not in NORMAL_MODELS:
            raise ValueError(f"Model {model_name} is not supported")
        self.model_name = model_name
        self.model = None

    def model_ready(self):
        if self.model is None:
            # Load model
            self.model = self.load_model()

    def load_model(self):
        if self.model_name == BERT:
            return SentenceTransformer("all-MiniLM-L6-v2")
        raise ValueError(f"Model {self.model_name} is not implemented")

    def run_model(self, model_input):
        if self.model_name == BERT:
            result = self.model.encode(model_input)
            return result.tolist()
        raise ValueError(f"Model {self.model_name} is not implemented")
