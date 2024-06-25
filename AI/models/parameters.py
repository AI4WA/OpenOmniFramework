from pydantic import BaseModel, Field


class Text2SpeechParameters(BaseModel):
    text: str = Field(..., description="The text to convert to speech")


class Speech2TextParameters(BaseModel):
    audio_file_path: str = Field(..., description="The path to the audio file")
