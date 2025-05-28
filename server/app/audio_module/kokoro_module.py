from typing import Dict, Optional
from app.audio_module.audio_module import AudioModule, AudioResult
from app.services.kokoro.kokoro import KokoroGenerationConfig, KokoroService


class KokoroAudio(AudioModule):
    def __init__(self, max_chars: int = 5000):
        super().__init__(max_chars=max_chars)
        self.client = KokoroService(
            onnx_path="app/services/kokoro/kokoro-v1.0.onnx",
            voices_path="app/services/kokoro/voices-v1.0.bin",
        )

    def generate_audio(
        self,
        text: str,
        file_path: str,
        voice: str = "am_michael",
        voice_settings: Optional[Dict] = None,
    ) -> AudioResult:
        config = KokoroGenerationConfig(file_path=file_path, voice=voice)
        self.client.generate_audio(text, config)

    def get_voices(self) -> list[str]:
        return []
