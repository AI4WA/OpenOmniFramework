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
