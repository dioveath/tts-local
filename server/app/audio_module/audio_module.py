from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel


class AudioResult(BaseModel):
    file_path: str
    length: float  # in seconds


class AudioModule(ABC):
    client = None
    
    def __init__(self, max_chars: int = 2500):
        self.max_chars = max_chars

    @abstractmethod
    def generate_audio(
        self, text: str, file_path: str, voice: Optional[str], voice_settings: Optional[dict]
    ) -> AudioResult:
        pass

    @abstractmethod
    def get_voices(self) -> list[str]:
        pass
