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
    openai_speech2text = "openai_speech2text"
    openai_gpt4o = "openai_gpt_4o"
    openai_text2speech = "openai_text2speech"
    openai_gpt_35 = "openai_gpt_35"
    openai_gpt4o_text_only = "openai_gpt_4o_text_only"
    openai_gpt_4o_text_and_image = "openai_gpt_4o_text_and_image"
    rag = "rag"


class ResultStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    started = "started"
    cancelled = "cancelled"


class TaskResultJSON(BaseModel):
    result_profile: Dict = Field(default_factory=dict, description="The result profile")
    latency_profile: Dict = Field(
        default_factory=dict, description="The latency profile"
    )


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
    parameters: dict = Field(
        default_factory=dict, description="The parameters for the task"
    )
    result_status: ResultStatus = Field(
        ResultStatus.pending, description="The status of the task"
    )
    result_json: TaskResultJSON = Field(
        default_factory=lambda: TaskResultJSON(result_profile={}, latency_profile={}),
        description="The result of the task",
    )
    description: Optional[str] = Field(
        None, description="The description of the task result"
    )
