"""
pip install -U kokoro-onnx soundfile

wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
python examples/save.py
"""

from typing import Optional
from kokoro_onnx import Kokoro
from pydantic import BaseModel
import soundfile as sf


class KokoroGenerationConfig(BaseModel):
    text: str
    voice: Optional[str] = "am_michael"
    speed: Optional[float] = 1
    lang: Optional[str] = "en-us"

class KokoroService:
    def __init__(self) -> None:
        self.kokoro = Kokoro(
            "app/services/kokoro/kokoro-v1.0.onnx",
            "app/services/kokoro/voices-v1.0.bin"
        )

    def generate_audio(self, output_path: str, config: KokoroGenerationConfig):        
        print(f"Generating audio with Kokoro: {config.model_dump(mode='json')}")
        samples, sample_rate = self.kokoro.create(config.text, voice=config.voice, speed=config.speed, lang=config.lang)
        sf.write(output_path, samples, sample_rate)

    @staticmethod
    def get_voices() -> list[str]:
        return KokoroService().kokoro.get_voices()
