import os
from datetime import datetime


class ProcessLogger:
    LEVELS = {"errors": 0, "normal": 1, "detailed": 2}

    def __init__(self, log_folder: str, level: str = "normal"):
        self.log_folder = log_folder
        self.level = (level or "normal").lower()
        os.makedirs(log_folder, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_path = os.path.join(log_folder, f"log_{timestamp}.txt")

    def _write(self, level_name: str, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_path, "a", encoding="utf-8") as file:
            file.write(f"[{timestamp}] [{level_name}] {message}\n")

    def info(self, message: str) -> None:
        if self.LEVELS.get(self.level, 1) >= 1:
            self._write("INFO", message)

    def debug(self, message: str) -> None:
        if self.LEVELS.get(self.level, 1) >= 2:
            self._write("DEBUG", message)

    def error(self, message: str) -> None:
        self._write("ERROR", message)