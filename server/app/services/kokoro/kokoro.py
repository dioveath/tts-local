# """
# pip install -U kokoro-onnx soundfile

# wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
# wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
# python examples/save.py
# """

# from typing import Optional
# from kokoro_onnx import Kokoro
# from pydantic import BaseModel
# import soundfile as sf


# class KokoroGenerationConfig(BaseModel):
#     file_path: str
#     voice: Optional[str] = "am_michael"
#     speed: Optional[float] = 1
#     lang: Optional[str] = "en-us"


# class KokoroService:
#     def __init__(self, onnx_path: str, voices_path: str) -> None:
#         self.kokoro = Kokoro(onnx_path, voices_path)

#     def generate_audio(self, text: str, config: KokoroGenerationConfig):
#         samples, sample_rate = self.kokoro.create(text, voice=config.voice, speed=config.speed, lang=config.lang)
#         sf.write(config.file_path, samples, sample_rate)

#     def get_voices() -> list[str]:
#         return []
