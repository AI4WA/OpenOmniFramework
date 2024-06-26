from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field


class TaskName(str, Enum):
    quantization_llm = "quantization_llm"
    hf_llm = "hf_llm"
    emotion_detection = "emotion_detection"
    speech2text = "speech2text"
    text2speech = "text2speech"
    general_ml = "general_ml"


class ResultStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    started = "started"
    cancelled = "cancelled"


class Task(BaseModel):
    """
    The Task Model
    This is the one we will pull and ask for the task from the API
    """

    id: int = Field(description="The ID of the task")
    name: str = Field(description="A unique name to track the cluster of tasks")
    user_id: Optional[int] = Field(
        None, description="The ID of the user who created the task"
    )
    task_name: TaskName = Field(description="The name of the task")
    parameters: dict = Field(dict, description="The parameters for the task")
    result_status: ResultStatus = Field(
        ResultStatus.pending, description="The status of the task"
    )
    result_json: Optional[Dict] = Field(None, description="The result of the task")
    description: Optional[str] = Field(
        None, description="The description of the task result"
    )
