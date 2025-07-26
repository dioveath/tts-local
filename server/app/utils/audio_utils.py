import subprocess
import logging

logger = logging.getLogger(__name__)

def get_audio_duration(file_path: str) -> float:
    try:
        command = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError) as e:
        logger.error(f"Error getting audio duration: {e}")
        return 0.0