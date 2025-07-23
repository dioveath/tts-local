# app/tasks.py
from typing import Dict, Optional
import pyttsx3
from celery import Task, states
from celery.result import AsyncResult
from celery.exceptions import Ignore
import logging
import pathlib
import time
import gc
import os

from app.audio_module.pyttsx_module import PyttsxModule
from app.audio_module.kokoro_module import KokoroAudio
# from app.audio_module.chatterbox_module import ChatterboxModule
from app.celery_worker import celery_app
from app.config import settings
from app.services.minio.minio_client import minio_client, minio_public_endpoint, bucket_name
from app.services.subtitles.subtitle_generator import SubtitleGenerator
from app.schemas import EngineOptions, CaptionSettings
from app.utils.webhook import send_webhook_task

logger = logging.getLogger(__name__)




@celery_app.task(bind=True, name='app.tasks.generate_audio_task', acks_late=True)
def generate_audio_task(
    self: Task, 
    engine: str, 
    text: str, 
    engine_options: Optional[Dict], 
    output_format: str, 
    caption_settings: Optional[CaptionSettings],
    webhook_url: Optional[str] = None
):
    task_id = self.request.id
    logger.info(f"[Task {task_id}] Received task - Engine: {engine}, Format: {output_format}")

    output_dir = settings.output_audio_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    file_extension = output_format # TODO: Add more formats later
    output_filename = f"{task_id}.{file_extension}"
    output_path = output_dir / output_filename

    result = {
        # "output_path": str(output_path),
        "output_url": None,
        "subtitle_url": None,
        "engine": engine,
        "format": file_extension
    }

    audio_engine = None

    try:
        self.update_state(state=states.STARTED)
        logger.info(f"[Task {task_id}] Generating audio with engine: {engine}")
                
        if engine == "pyttsx3":
            audio_engine = PyttsxModule()
            audio_engine.generate_audio(text, output_path.as_posix(), engine_options)
            # Ignore()
        elif engine == "kokoro":
            audio_engine = KokoroAudio()
            audio_engine.generate_audio(text, output_path.as_posix(), voice_settings=engine_options)
        # elif engine == "chatterbox":
        #     chatterbox_engine = ChatterboxModule()
        #     voice = engine_options.get("voice", "am_michael") if engine_options else "am_michael"
        #     chatterbox_engine.generate_audio(text, output_path.as_posix(), voice_settings=engine_options)
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

        result["output_url"] = output_url

        # TODO: Add caption generation logic here
        if caption_settings:
            subtitle_generator = None
            try:
                subtitle_generator = SubtitleGenerator()
                subtitle_path = output_path.with_suffix('.ass')
                subtitle_generator.generate_subtitles(output_path.as_posix(), subtitle_path, caption_settings)
                minio_client.fput_object(bucket_name, subtitle_path.name, subtitle_path.as_posix())
                subtitle_url = f"{minio_public_endpoint}/{bucket_name}/{subtitle_path.name}"
                result["subtitle_url"] = str(subtitle_url)
            except Exception as e:
                logger.error(f"[Task {task_id}] Subtitle generation failed: {e}", exc_info=True)
                self.update_state(
                    state=states.FAILURE,
                    meta={'exc_type': type(e).__name__, 'exc_message': str(e)}
                )
                Ignore()
            finally:
                if subtitle_generator:
                    subtitle_generator.unload_model()
                    del subtitle_generator
                    gc.collect()
        
        logger.info(f"[Task {task_id}] Task completed successfully. Output: {output_path}")
        self.update_state(
            state=states.SUCCESS,
            meta=result
        )
        return result

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
    finally:
        # Delete local file after successful upload to MinIO
        if output_path:
            try:
                os.remove(output_path)
            except OSError as e:
                logger.error(f"[Task {task_id}] Failed to delete local file {output_path}: {e}", exc_info=True)
        
        if audio_engine:
            del audio_engine
            gc.collect()

        if webhook_url:
            current_task_state = AsyncResult(task_id)
            payload = {
                "task_id": task_id,
                "task_state": current_task_state.state,
                "task_info": current_task_state.info,
                "result": result
            }
            send_webhook_task(webhook_url, payload, task_id)
            pass