# app/tasks.py
from typing import Dict, Optional
import pyttsx3
from celery import Task, states
from celery.exceptions import Ignore
import logging
import pathlib
import time

from app.audio_module.kokoro_module import KokoroAudio
from app.celery_worker import celery_app
from app.config import settings
from app.services.minio.minio_client import minio_client, minio_public_endpoint, bucket_name

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def _generate_pyttsx3(task: Task, text: str, engine_options: Optional[Dict], output_path: pathlib.Path):
    logger.info(f"[Task {task.request.id}] Starting pyttsx3 generation for: {output_path}")
    engine_options = engine_options or {}
    try:
        engine = pyttsx3.init()

        rate = engine_options.get("rate")
        if rate:
            engine.setProperty('rate', int(rate))

        volume = engine_options.get("volume")
        if volume is not None:
             engine.setProperty('volume', float(volume))

        voice_id = engine_options.get("voice_id")
        if voice_id:
            voices = engine.getProperty('voices')
            found_voice = next((v for v in voices if v.id == voice_id), None)
            if found_voice:
                 engine.setProperty('voice', found_voice.id)
            else:
                 logger.warning(f"[Task {task.request.id}] Voice ID '{voice_id}' not found. Using default.")

        engine.save_to_file(text, str(output_path))
        engine.runAndWait()
        engine.stop()
        logger.info(f"[Task {task.request.id}] pyttsx3 generation successful: {output_path}")

    except Exception as e:
        logger.error(f"[Task {task.request.id}] pyttsx3 generation failed: {e}", exc_info=True)
        task.update_state(
            state=states.FAILURE,
            meta={'exc_type': type(e).__name__, 'exc_message': str(e)}
        )
        raise Ignore()


@celery_app.task(bind=True, name='app.tasks.generate_audio_task', acks_late=True)
def generate_audio_task(self: Task, engine: str, text: str, engine_options: Optional[Dict], output_format: str):
    task_id = self.request.id
    logger.info(f"[Task {task_id}] Received task - Engine: {engine}, Format: {output_format}")

    output_dir = settings.output_audio_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    file_extension = output_format if output_format in ['mp3', 'wav'] else 'mp3'
    output_filename = f"{task_id}.{file_extension}"
    output_path = output_dir / output_filename

    try:
        if engine == "pyttsx3":
            _generate_pyttsx3(self, text, engine_options, output_path)
        elif engine == "kokoro":
            kokoro_engine = KokoroAudio()
            voice = engine_options.get("voice", "am_michael") if engine_options else "am_michael"
            kokoro_engine.generate_audio(text, output_path.as_posix(), voice=voice, voice_settings=engine_options)
            
        else:
            logger.error(f"[Task {task_id}] Unsupported engine specified: {engine}")
            self.update_state(
                state=states.FAILURE,
                meta={'exc_type': 'ValueError', 'exc_message': f"Unsupported engine: {engine}"}
            )
            raise Ignore()

        if not output_path.is_file():
             logger.error(f"[Task {task_id}] Output file not found after generation: {output_path}")
             self.update_state(
                state=states.FAILURE,
                meta={'exc_type': 'FileNotFoundError', 'exc_message': f"Generated file missing: {output_path}"}
            )
             raise Ignore()

        minio_client.fput_object(bucket_name, output_filename, output_path.as_posix())
        output_url = f"{minio_public_endpoint}/{bucket_name}/{output_filename}"

        # Delete local file after successful upload to MinIO
        output_path.unlink()
        
        logger.info(f"[Task {task_id}] Task completed successfully. Output: {output_path}")
        return {
            "output_path": str(output_path),
            "output_url": str(output_url),
            "engine": engine,
            "format": file_extension,
            "timestamp": time.time()
        }

    except Ignore:
        raise

    except Exception as exc:
        logger.error(f"[Task {task_id}] Unhandled exception in generate_audio_task: {exc}", exc_info=True)
        self.update_state(
            state=states.FAILURE,
            meta={
                'exc_type': type(exc).__name__,
                'exc_message': str(exc),
                'traceback': self.app.backend.prepare_exception(exc, self.request.id)
            }
        )
        raise