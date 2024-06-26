from typing import List

from pydantic import BaseModel, Field


class Text2SpeechParameters(BaseModel):
    text: str = Field(..., description="The text to convert to speech")


class Speech2TextParameters(BaseModel):
    uid: str = Field(..., description="The uid of the audio acquire session")
    audio_index: str = Field(..., description="The sequence index of the audio")
    end_time: str = Field(..., description="The end time of the audio")


class EmotionDetectionParameters(BaseModel):
    text: str = Field(..., description="The text to analyze for emotion")
    audio_file: str = Field(..., description="The audio data to analyze for emotion")
    images_path_list: List[str] = Field(
        description="The images data to analyze for emotion"
    )
    data_text_id: int = Field(..., description="The id of the data text")


class QuantizationLLMParameters(BaseModel):
    prompt: str = Field(..., description="The text to analyze for quantization")
    llm_model_name: str = Field(..., description="The name of the llm model")


class HFParameters(BaseModel):
    text: str = Field(..., description="The text to analyze for HFP")
    task: str = Field(default="text-generation", description="The task, can be others")
    hf_model_name: str = Field(..., description="The name of the hf model")


class GeneralMLParameters(BaseModel):
    text: str = Field(..., description="The text to analyze for general ML")
    general_model_name: str = Field(..., description="The name of the model")
    params: dict = Field({}, description="The parameters of the model")
