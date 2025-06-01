from typing import Optional, Dict
from app.audio_module.audio_module import AudioModule, AudioResult
from app.services.chatterbox.chatterbox import ChatterboxService, ChatterboxGenerationConfig
from app.utils.text_utils import split_text_into_chunks
import subprocess
import tempfile
import os
import uuid
import logging

logger = logging.getLogger(__name__)

class ChatterboxModule(AudioModule):
    def __init__(self, max_chars: int = 500):
        super().__init__(max_chars=max_chars)
        self.client = ChatterboxService()

    def generate_audio(
        self,
        text: str,
        file_path: str,
        voice_settings: Optional[Dict] = None,
    ) -> AudioResult:
        if voice_settings is None:
            voice_settings = {}
        exaggeration = voice_settings.get("exaggeration", 0.25)
        cfg_weight = voice_settings.get("cfg_weight", 0.3)
        temperature = voice_settings.get("temperature", 0.8)
        config = ChatterboxGenerationConfig(
            text=text, 
            exaggeration=exaggeration, 
            cfg_weight=cfg_weight, 
            temperature=temperature
        )
        logger.info(f"Generating audio with Chatterbox: {config}")

        split_text = split_text_into_chunks(text, self.max_chars)
        logger.info(f"Splitted text into {len(split_text)} chunks")

        if len(split_text) == 1:
            self.client.generate(file_path, config)
            return AudioResult(file_path=file_path, length=0)
        
        temp_files = []
        for i, text in enumerate(split_text):
            temp_file = os.path.join(tempfile.gettempdir(), f"temp_chatterbox_{uuid.uuid4()}.wav")
            logging.info(f"Generating audio for chunk {i+1}/{len(split_text)} - {str(temp_file)}")
            logging.info(f"Text: {text}")
            config.text = text
            self.client.generate(temp_file, config)
            temp_files.append(temp_file)

        logger.info("Combining audio files")
        self._combine_audio_files(temp_files, file_path)

        logger.info("Cleaning up temporary files")
        for temp_file in temp_files:
            os.remove(temp_file) 
        
        return AudioResult(file_path=file_path, length=0)

    def _combine_audio_files(self, input_files: list[str], output_file: str):
        try:
            temp_list_file = os.path.join(tempfile.gettempdir(), f"ffmpeg_concat_{uuid.uuid4()}.txt")
            with open(temp_list_file, 'w') as f:
                for file in input_files:
                    f.write(f"file '{file}'\n")
            
            ffmpeg_cmd = [
                "ffmpeg",
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", temp_list_file,
                "-c", "copy",
                output_file
            ]

            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)

            try:
                os.remove(temp_list_file)
            except Exception as e:
                logger.info(f"Error removing temporary file {temp_list_file}: {e}")
                pass

        except subprocess.CalledProcessError as e:
            logger.info(f"FFmpeg command failed with return code {e.returncode}")
            logger.info(f"FFmpeg command: {str(ffmpeg_cmd)}")
            logger.info(f"Error output: {e.stderr}")
            return False
        except Exception as e:
            logger.info(f"Error combining audio files: {e}")
            return False
        
        

    def get_voices(self) -> list[str]:
        return []