import os
import torch
import time
import torchaudio as ta
from pydantic import BaseModel, Field
from typing import Optional
from chatterbox.tts import ChatterboxTTS
import logging

logger = logging.getLogger(__name__)


class ChatterboxGenerationConfig(BaseModel):
    text: str
    audio_prompt_path: Optional[str] = None
    exaggeration: Optional[float] = Field(0.5, ge=0.25, le=2.0)
    cfg_weight: Optional[float] = Field(0.3, ge=0.2, le=1.0)
    temperature: Optional[float] = Field(0.8, ge=0.05, le=5.0)

class ChatterboxService:
    VOICES_DIR = os.path.join(os.path.dirname(__file__), "voices")

    def __init__(self) -> None:
        logger.info("Loading Chatterbox model...")
        start_time = time.time()

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        self.model = ChatterboxTTS.from_pretrained(device=self.device)

        end_time = time.time()
        load_time = end_time - start_time
        logger.info(f"Loaded Chatterbox model in {load_time:.2f} seconds")

        self.voices_dir = os.path.join(os.path.dirname(__file__), "voices")

    def generate(self, output_path: str, generation_config: ChatterboxGenerationConfig):
        with torch.no_grad():
            wav = self.model.generate(
                generation_config.text, 
                audio_prompt_path=generation_config.audio_prompt_path, 
                exaggeration=generation_config.exaggeration, 
                cfg_weight=generation_config.cfg_weight, 
                temperature=generation_config.temperature
            )

        ta.save(output_path, wav, self.model.sr)
        logger.info(f"Saved generated audio to {output_path}")

        if (self.device == "cuda"):
            if hasattr(self.model, 'clear_cache'):
                self.model.clear_cache()
                logger.info(f"Cleared cache after generation using {self.model.clear_cache.__name__}")

            del wav
            torch.cuda.empty_cache()
            logger.info(f"Cleaned up GPU VRAM after generation")

    @staticmethod
    def get_voices() -> list[str]:
        # find .wav files in voices folder, return the list excluding the .wav extension
        if not os.path.isdir(ChatterboxService.VOICES_DIR):
            logger.warning("Voices directory not found")
            return []
        voice_files = [f for f in os.listdir(ChatterboxService.VOICES_DIR) if f.endswith(".wav")]
        voice_names = [os.path.splitext(f)[0] for f in voice_files]
        return voice_names

# text = "Ezreal and Jinx teamed up with Ahri, Yasuo, and Teemo to take down the enemy's Nexus in an epic late-game pentakill."
# wav = model.generate(text)
# ta.save("test-1.wav", wav, model.sr)

# # If you want to synthesize with a different voice, specify the audio prompt
# AUDIO_PROMPT_PATH="YOUR_FILE.wav"
# wav = model.generate(text, audio_prompt_path=AUDIO_PROMPT_PATH)
# ta.save("test-2.wav", wav, model.sr)