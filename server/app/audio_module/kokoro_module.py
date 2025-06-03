from typing import Dict, Optional
from app.audio_module.audio_module import AudioModule, AudioResult
from app.services.kokoro.kokoro import KokoroGenerationConfig, KokoroService


class KokoroAudio(AudioModule):
    def __init__(self, max_chars: int = 5000):
        super().__init__(max_chars=max_chars)
        self.client = KokoroService()

    def generate_audio(
        self,
        text: str,
        file_path: str,
        voice_settings: Optional[Dict] = None,
    ) -> AudioResult:
        if voice_settings is None:
            voice_settings = {}

        voice = voice_settings.get("voice", "am_michael")
        speed = voice_settings.get("speed", 1)
        lang = voice_settings.get("lang", "en-us")

        config = KokoroGenerationConfig(text=text, voice=voice)
        self.client.generate_audio(output_path=file_path, config=config)

    def get_voices(self) -> list[str]:
        return KokoroService.get_voices()
