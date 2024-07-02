from pydantic import BaseModel, Field


class Speech2TextResult(BaseModel):
    text: str = Field(..., description="The text result of the speech to text")
    # also allow other fields in
    logs = Field({}, description="The logs of the speech to text")


class EmotionDetectionResult(BaseModel):
    emotion: str = Field(..., description="The emotion result of the text")
    # also allow other fields in
    logs = Field({}, description="The logs of the emotion detection")