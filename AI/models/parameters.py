from pydantic import BaseModel, Field


class Text2SpeechParameters(BaseModel):
    text: str = Field(..., description="The text to convert to speech")


class Speech2TextParameters(BaseModel):
    uid: str = Field(..., description="The uid of the audio acquire session")
    audio_index: str = Field(..., description="The sequence index of the audio")
    end_time: str = Field(..., description="The end time of the audio")
