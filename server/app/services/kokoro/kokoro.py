"""
pip install -U kokoro-onnx soundfile

wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
python examples/save.py
"""

import time
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
        try:
            self.kokoro = Kokoro(
                "app/services/kokoro/kokoro-v1.0.onnx",
                "app/services/kokoro/voices-v1.0.bin",
                providers=['CUDAExecutionProvider']
            )
            print(f"Loaded Kokoro model with CUDA")
        except Exception as e:
            self.kokoro = Kokoro(
                "app/services/kokoro/kokoro-v1.0.onnx",
                "app/services/kokoro/voices-v1.0.bin",
            )
            print(f"Loaded Kokoro model with CPU")

    def generate_audio(self, output_path: str, config: KokoroGenerationConfig):        
        print(f"Generating audio with Kokoro: {config.model_dump(mode='json')}")
        start_time = time.time()
        samples, sample_rate = self.kokoro.create(config.text, voice=config.voice, speed=config.speed, lang=config.lang)
        sf.write(output_path, samples, sample_rate)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Generated audio in {elapsed_time:.2f} seconds")

    @staticmethod
    def get_voices() -> list[str]:
        return KokoroService().kokoro.get_voices()
