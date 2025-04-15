# app/config.py
import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import DirectoryPath, AnyUrl, SecretStr
import pathlib


OUTPUT_AUDIO_DIR = pathlib.Path("./output_audio")

if not os.path.isdir(OUTPUT_AUDIO_DIR):
    os.makedirs(OUTPUT_AUDIO_DIR, exist_ok=True)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore'
    )

    celery_broker_url: AnyUrl = "redis://localhost:6379/0"
    celery_result_backend: str = "db+sqlite:///./celery_results.db"
    
    output_audio_dir: DirectoryPath = pathlib.Path("./output_audio")

    elevenlabs_api_key: Optional[SecretStr] = None



settings = Settings()
