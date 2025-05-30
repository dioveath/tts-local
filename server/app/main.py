# app/main.py
import pathlib
from fastapi import FastAPI, HTTPException, Request, status as http_status, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import AudioGenerationRequest, TaskSubmissionResponse, TaskStatusResponse
from app.celery_worker import celery_app
from celery.result import AsyncResult
from celery import states
import logging
import uvicorn

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Asynchronous AI Audio Generation API",
    description="Submit and manage AI audio generation tasks.",
    version="0.1.0"
)

origins = [
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://192.168.1.87:5174",
    # Add your production frontend URL here if applicable
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/", tags=["General"])
async def read_root():
    return {"message": "Welcome to the AI Audio Generation API"}


@app.get("/health", status_code=http_status.HTTP_200_OK, tags=["General"])
async def health_check():
    return {"status": "ok"}


@app.post(
    "/generate/audio",
    response_model=TaskSubmissionResponse,
    status_code=http_status.HTTP_202_ACCEPTED,
    tags=["Audio Generation"]
)
async def submit_audio_generation(
    request: Request,
    payload: AudioGenerationRequest
):
    try:
        actual_backend_url = celery_app.conf.get('result_backend')
        logger.info(f"Celery app result backend: {actual_backend_url}")
        logger.info(f"Type of configured backend: {type(actual_backend_url)}")

        actual_broker_url = celery_app.conf.get('broker_url')
        logger.info(f"Celery app broker URL: {actual_broker_url}")
        logger.info(f"Type of configured broker URL: {type(actual_broker_url)}")

        caption_settings_args = payload.caption_settings.model_dump(mode='json') if payload.caption_settings else None

        task = celery_app.send_task(
            'app.tasks.generate_audio_task',
            args=[
                payload.engine,
                payload.text,
                payload.engine_options,
                payload.output_format,
                caption_settings_args
            ],
        )
        task_id = task.id
        logger.info(f"Submitted task {task_id} for engine '{payload.engine}'.")

    except Exception as e:
        logger.error(f"Failed to submit task to Celery: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit task to queue: {e}"
        )

    base_url = str(request.base_url)
    status_url = f"{base_url}tasks/{task_id}"

    return TaskSubmissionResponse(task_id=task_id, status_url=status_url)


@app.get(
    "/tasks/{task_id}",
    response_model=TaskStatusResponse,
    tags=["Task Management"]
)
async def get_task_status(task_id: str):
    logger.debug(f"Querying status for task_id: {task_id}")
    task_result = AsyncResult(task_id, app=celery_app)

    current_status = task_result.status
    result_data = None
    error_info = None

    if task_result.successful():
        current_status = states.SUCCESS
        result_data = task_result.get()
        logger.debug(f"Task {task_id} succeeded. Result: {result_data}")
    elif task_result.failed():
        current_status = states.FAILURE
        error_info = str(task_result.result)
        logger.error(f"Task {task_id} failed. Error: {error_info}")
        # Attempt to get more structured error info if stored in meta
        try:
            meta = task_result.info
            if isinstance(meta, dict) and 'exc_type' in meta:
                 error_info = f"{meta.get('exc_type', 'Error')}: {meta.get('exc_message', 'Unknown')}"
        except Exception:
             pass # Fallback to default error info string
    elif current_status == states.PENDING:
        logger.debug(f"Task {task_id} is PENDING (or possibly unknown).")
    elif current_status in [states.STARTED, states.RETRY]:
        logger.debug(f"Task {task_id} status: {current_status}")
    else:
        logger.warning(f"Task {task_id} has an unexpected status: {current_status}")

    return TaskStatusResponse(
        task_id=task_id,
        status=current_status,
        result=result_data,
        error=error_info
    )

@app.get("/audio/{task_id}", tags=["Audio Generation"])
async def download_audio_file(task_id: str):
    logger.info(f"Download request for task_id: {task_id}")
    task_result = AsyncResult(task_id, app=celery_app)

    if not task_result.ready():
        status = task_result.status
        logger.warning(f"Task {task_id} is not ready. Status: {status}")
        detail = f"Task not yet complete (Status: {status}). Please try again later."
        status_code = http_status.HTTP_409_CONFLICT
        raise HTTPException(status_code=status_code, detail=detail)
    
    if task_result.status != states.SUCCESS:
        logger.error(f"Task {task_id} did not complete successfully. Status: {task_result.status}")
        error_detail = f"Task failed (Status: {task_result.status})."
        error_detail += f" Error: {task_result.info.get('exc_type', '')} - {task_result.info.get('exc_message', '')}"

        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, # Or 500 depending on how you want to report failures
            detail=error_detail
        )
    
    result_data = task_result.get()
    if not isinstance(result_data, dict) or "output_path" not in result_data:
        logger.error(f"Task {task_id} succeeded but result format is unexpected: {result_data}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Task completed but result data is missing the file path."
        )
    
    file_path_str = result_data["output_path"]
    file_path = pathlib.Path(file_path_str)

    return FileResponse(path=file_path, media_type="audio", filename=file_path.name)


@app.delete("/tasks/{task_id}", response_model=TaskStatusResponse, status_code=http_status.HTTP_200_OK, tags=["Task Management"])
async def stop_task(
    task_id: str,
    terminate: bool = Query(False, description="Set to true to attempt terminating a running task (sends SIGTERM). Requires process-based pool."),
    signal: str = Query("TERM", description="Signal to send if terminate=true (e.g., TERM, KILL). Use KILL with extreme caution.")
):
    """
    Revokes or terminates a Celery task.

    - By default (`terminate=false`), prevents the task from running if pending.
    - If `terminate=true`, attempts to stop a *currently running* task by sending a signal (default SIGTERM).
      This works best with the 'prefork' pool and is not guaranteed to succeed immediately or cleanly.
    - Using `terminate=true` with `signal=KILL` forcefully terminates the task process, risking data loss.
    """
    logger.info(f"Received request to stop task {task_id} (terminate={terminate}, signal={signal})")

    if terminate and signal.upper() not in ('TERM', 'KILL'):
         raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Invalid signal specified. Use 'TERM' or 'KILL'."
         )

    try:
        celery_app.control.revoke(task_id, terminate=terminate, signal=signal.upper())
        message = f"Revoke command sent for task {task_id}."
        if terminate:
            message += f" Termination requested with signal {signal.upper()}."
        else:
            message += " Task will not be executed if still pending."

        logger.info(message)

        task_result = AsyncResult(task_id, app=celery_app)
        return TaskStatusResponse(
            task_id=task_id,
            status=task_result.status,
            result={"message": message}
        )

    except Exception as e:
        logger.error(f"Failed to send revoke command for task {task_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send revoke/terminate command for task {task_id}."
        )



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8100)