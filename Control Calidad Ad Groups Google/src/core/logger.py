import os
from datetime import datetime


def create_logger(logs_dir: str, run_id: str):

    os.makedirs(logs_dir, exist_ok=True)

    log_path = os.path.join(
        logs_dir,
        f"log_{run_id}.txt"
    )

    return log_path


def _write(log_path: str, level: str, message: str):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line = f"[{timestamp}] [{level}] {message}"

    # consola
    print(line)

    # fichero
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def log_info(logger, message):
    _write(logger, "INFO", message)


def log_error(logger, message):
    _write(logger, "ERROR", message)