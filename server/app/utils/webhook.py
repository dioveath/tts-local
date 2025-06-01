import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

def send_webhook_task(webhook_url: str, data: dict, task_id: Optional[str]) -> bool:
    """Send a webhook to the given URL with the given data."""
    try:
        response = requests.post(webhook_url, json=data, timeout=10)
        response.raise_for_status()
        logger.info(f"Successfully sent webhook notification to {webhook_url} for task {task_id}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send webhook notification to {webhook_url} for task {task_id}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred while sending webhook notification to {webhook_url} for task {task_id}: {str(e)}")
        return False