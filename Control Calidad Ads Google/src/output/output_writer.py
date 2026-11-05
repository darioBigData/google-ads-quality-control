import csv
import os
from datetime import datetime
from typing import Dict, List


class OutputWriter:
    def __init__(self, resumen_folder: str, errores_folder: str, delimiter: str = ";"):
        self.resumen_folder = resumen_folder
        self.errores_folder = errores_folder
        self.delimiter = delimiter

        os.makedirs(self.resumen_folder, exist_ok=True)
        os.makedirs(self.errores_folder, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.resumen_file = os.path.join(self.resumen_folder, f"output_resumen_ads{timestamp}.csv")
        self.errores_file = os.path.join(self.errores_folder, f"output_errores_ads{timestamp}.csv")

    def write_resumen(self, rows: List[Dict], fieldnames: List[str]) -> None:
        self._write_csv(self.resumen_file, rows, fieldnames)

    def write_errores(self, rows: List[Dict], fieldnames: List[str]) -> None:
        self._write_csv(self.errores_file, rows, fieldnames)

    def _write_csv(self, file_path: str, rows: List[Dict], fieldnames: List[str]) -> None:
        with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=self.delimiter)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)