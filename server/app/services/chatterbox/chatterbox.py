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
    def __init__(self) -> None:
        logger.info("Loading Chatterbox model...")
        start_time = time.time()

        device = "cpu"
        map_location = torch.device(device)

        torch_load_original = torch.load
        def patched_torch_load(*args, **kwargs):
            if 'map_location' not in kwargs:
                kwargs['map_location'] = map_location
            return torch_load_original(*args, **kwargs)
        torch.load = patched_torch_load

        self.model = ChatterboxTTS.from_pretrained(device=device)

        end_time = time.time()
        load_time = end_time - start_time
        logger.info(f"Loaded Chatterbox model in {load_time:.2f} seconds")

    def generate(self, output_path: str, generation_config: ChatterboxGenerationConfig):
        wav = self.model.generate(
            generation_config.text, 
            audio_prompt_path=generation_config.audio_prompt_path, 
            exaggeration=generation_config.exaggeration, 
            cfg_weight=generation_config.cfg_weight, 
            temperature=generation_config.temperature
        )
        ta.save(output_path, wav, self.model.sr)

    def get_voices() -> list[str]:
        return []

# text = "Ezreal and Jinx teamed up with Ahri, Yasuo, and Teemo to take down the enemy's Nexus in an epic late-game pentakill."
# wav = model.generate(text)
# ta.save("test-1.wav", wav, model.sr)

# If you want to synthesize with a different voice, specify the audio prompt
# AUDIO_PROMPT_PATH="YOUR_FILE.wav"
# wav = model.generate(text, audio_prompt_path=AUDIO_PROMPT_PATH)
# ta.save("test-2.wav", wav, model.sr)