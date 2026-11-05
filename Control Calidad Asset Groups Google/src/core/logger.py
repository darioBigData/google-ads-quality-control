import os
from datetime import datetime


def create_logger(logs_dir: str, run_id: str):

    os.makedirs(logs_dir, exist_ok=True)

    log_file = os.path.join(logs_dir, f"log_{run_id}.txt")

    return {
        "file": log_file
    }


def _write(logger, level: str, message: str):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line = f"[{timestamp}] [{level}] {message}"

    with open(logger["file"], "a", encoding="utf-8") as f:
        f.write(line + "\n")


def log_info(logger, message: str):
    _write(logger, "INFO", message)


def log_error(logger, message: str):
    _write(logger, "ERROR", message)