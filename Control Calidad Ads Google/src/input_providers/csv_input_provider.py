import csv
import os
from typing import Dict, List

from core.control_validator import validate_input_headers


class CsvInputProvider:
    def __init__(self, file_path: str, delimiter: str = ";"):
        self.file_path = file_path
        self.delimiter = delimiter

    def read_rows(self, max_rows: int) -> List[Dict[str, str]]:
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"No existe el input: {self.file_path}")

        with open(self.file_path, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file, delimiter=self.delimiter)
            validate_input_headers(reader.fieldnames)

            rows = []
            for index, row in enumerate(reader, start=1):
                if index > max_rows:
                    break

                normalized = {
                    "customer_id": (row.get("customer_id") or "").strip(),
                    "campaign_id": (row.get("campaign_id") or "").strip(),
                    "ad_group_id": (row.get("ad_group_id") or "").strip()
                }

                if not normalized["customer_id"]:
                    raise ValueError(f"La fila {index} no tiene customer_id.")

                rows.append(normalized)

        return rows