# app/celery_worker.py
import os
from celery import Celery
from app.config import settings

celery_broker_url_str = str(settings.celery_broker_url) if settings.celery_broker_url else None
celery_result_backend_str: str = "redis://localhost:6379/1"

print(f"--- Initializing Celery ---") # Add print for visibility
print(f"Broker URL for Celery init: '{celery_broker_url_str}' (Type: {type(celery_broker_url_str)})")
print(f"Backend URL for Celery init: '{celery_result_backend_str}' (Type: {type(celery_result_backend_str)})")
print(f"--- End Celery Init Args ---")

os.environ.setdefault("FORKED_BY_MULTIPROCESSING", "1")  # Required for Windows
celery_app = Celery(
    "audio_tasks", # Arbitrary name for the task namespace
    broker=celery_broker_url_str,
    backend=celery_result_backend_str,
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