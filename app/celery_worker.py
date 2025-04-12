# app/celery_worker.py
import os
from celery import Celery
from app.config import settings

celery_broker_url_str = str(settings.celery_broker_url) if settings.celery_broker_url else None

os.environ.setdefault("FORKED_BY_MULTIPROCESSING", "1")  # Required for Windows
celery_app = Celery(
    "audio_tasks", # Arbitrary name for the task namespace
    broker=celery_broker_url_str,
    backend=settings.celery_result_backend,
    include=["app.tasks"] # List of modules where tasks are defined
)

celery_app.conf.update(
    task_track_started=True,
    result_expires=3600,
    broker_connection_retry_on_startup=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
)
