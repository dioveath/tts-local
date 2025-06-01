import platform
import pyttsx3
from typing import Optional, Dict
from app.audio_module.audio_module import AudioModule, AudioResult
import logging

logger = logging.getLogger(__name__)

class PyttsxModule(AudioModule):
    def __init__(self):
        driver_name = None
        system = platform.system().lower()

        if system == 'darwin':
            driver_name = 'nsss'
        elif system == 'linux':
            driver_name = 'espeak'
        elif system == 'windows':
            driver_name = 'sapi5'
        else:
            raise ValueError(f"Unsupported platform: {system}")
        
        if driver_name is not None:
            self.engine = pyttsx3.init(driverName=driver_name)
        else:
            logger.warning(f"No driver found for platform: {system}")
            raise ValueError(f"No driver found for platform: {system}")

    def generate_audio(self, text: str, output_path: str, engine_options: Optional[Dict] = None) -> AudioResult:
        engine_options = engine_options or {}
        rate = engine_options.get("rate")
        if rate:
            self.engine.setProperty('rate', int(rate))
        volume = engine_options.get("volume")
        if volume is not None:
            self.engine.setProperty('volume', float(volume))

        voice_id = engine_options.get("voice_id")
        if voice_id:
            logger.info(f"Setting voice to {voice_id}")
            voices = self.engine.getProperty('voices')
            found_voice = next((v for v in voices if v.id == voice_id), None)
            if found_voice:
                self.engine.setProperty('voice', found_voice.id)
            else:
                logger.error(f"Voice ID '{voice_id}' not found. Using default.")
                voices = self.engine.getProperty('voices')
                self.engine.setProperty('voice', voices[0].id)
        else:
            logger.info("No voice ID provided. Using default.")
            voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', voices[0].id)

        logger.info(f"Generating audio with pyttsx3. Output path: {output_path}")
        logger.info(f"Engine options: {engine_options}")
        logger.info(f"Text: {text}")
        self.engine.save_to_file(text, output_path)
        self.engine.runAndWait()
        logger.info(f"Audio generated successfully. Output path: {output_path}")
        return AudioResult(file_path=output_path, length=0)

    def get_voices(self) -> list[str]:
        voices = self.engine.getProperty('voices')
        return [v.id for v in voices]