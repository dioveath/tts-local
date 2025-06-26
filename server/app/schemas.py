# app/schemas.py
from pydantic import BaseModel, Field, HttpUrl
from typing import Literal, Dict, Any, Optional, Union


class EngineOptions(BaseModel):
    voice: str = Field(..., description="Voice to use for synthesis")

class KokoroOptions(EngineOptions):
    speed: float = Field(default=1, description="Speed of the synthesis")
    lang: str = Field(default="en-us", description="Language of the synthesis")

class ChatterboxOptions(EngineOptions):
    exaggeration: Optional[float] = Field(0.5, ge=0.25, le=2.0, description="Exaggeration of the synthesis")
    cfg_weight: Optional[float] = Field(0.3, ge=0.2, le=1.0, description="CFG weight of the synthesis")
    temperature: Optional[float] = Field(0.8, ge=0.05, le=5.0, description="Temperature of the synthesis")

class CaptionSettings(BaseModel):
    max_line_count: int
    max_line_length: int
    font_name: str
    font_size: int
    primary_colour: str
    secondary_colour: str
    outline_colour: str
    back_colour: str
    bold: int
    italic: int
    underline: int
    strikeout: int
    outline: int
    border_style: int
    alignment: int
    playres_x: int
    playres_y: int
    timer: int

class AudioGenerationRequest(BaseModel):
    engine: Literal["chatterbox", "kokoro", "pyttsx3"]
    text: str = Field(..., min_length=1, description="Text to synthesize")
    engine_options: Union[ChatterboxOptions, KokoroOptions, EngineOptions] = Field(default=None, description="Engine-specific options (e.g., voice_id, rate)")
    output_format: Literal["wav"] = Field(default="wav", description="Desired output audio format") # TODO: Add more formats
    caption_settings: Optional[CaptionSettings] = Field(default=None, description="Caption settings for the audio")
    webhook_url: Optional[str] = Field(default=None, description="Webhook URL to call upon task completion")


class TaskSubmissionResponse(BaseModel):
    task_id: str = Field(..., description="Unique ID of the submitted Celery task")
    status_url: HttpUrl = Field(..., description="URL to check the status of the task")


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str = Field(..., description="Current status of the task (e.g., PENDING, STARTED, SUCCESS, FAILURE)")
    result: Union[Dict[str, Any], str, None] = Field(default=None, description="Result of the task if successful (e.g., {'output_path': ...}) or error details")
    error: Optional[str] = Field(default=None, description="Error message if the task failed")