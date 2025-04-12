# app/schemas.py
from pydantic import BaseModel, Field, HttpUrl
from typing import Literal, Dict, Any, Optional, Union

class AudioGenerationRequest(BaseModel):
    engine: Literal["pyttsx3", "elevenlabs"]
    text: str = Field(..., min_length=1, description="Text to synthesize")
    engine_options: Optional[Dict[str, Any]] = Field(default=None, description="Engine-specific options (e.g., voice_id, rate)")
    output_format: Literal["mp3", "wav"] = Field(default="mp3", description="Desired output audio format")


class TaskSubmissionResponse(BaseModel):
    task_id: str = Field(..., description="Unique ID of the submitted Celery task")
    status_url: HttpUrl = Field(..., description="URL to check the status of the task")


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str = Field(..., description="Current status of the task (e.g., PENDING, STARTED, SUCCESS, FAILURE)")
    result: Union[Dict[str, Any], str, None] = Field(default=None, description="Result of the task if successful (e.g., {'output_path': ...}) or error details")
    error: Optional[str] = Field(default=None, description="Error message if the task failed")

