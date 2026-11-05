import os
import csv

def read_customer_ids_from_csv(input_cfg: dict) -> list[str]:
    csv_cfg = input_cfg.get("csv", {})
    path = csv_cfg.get("path")
    required_columns = csv_cfg.get("required_columns", [])

    if not path:
        raise ValueError("input.csv.path no definido")

    if not os.path.exists(path):
        raise FileNotFoundError(f"Input CSV no encontrado: {path}")

    customer_ids = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")

        for col in required_columns:
            if col not in reader.fieldnames:
                raise ValueError(f"El CSV no contiene la columna requerida: {col}")

        for row in reader:
            cid = row.get("customer_id")
            if cid:
                customer_ids.append(cid)

    return customer_ids
