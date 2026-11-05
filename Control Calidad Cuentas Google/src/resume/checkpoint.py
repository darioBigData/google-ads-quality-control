import os
import csv
from typing import Set
from datetime import datetime


def get_checkpoint_path(config: dict, run_id: str) -> str:
    state_dir = config["resume"]["state_dir"]
    filename_tpl = config["resume"]["checkpoint_file"]
    filename = filename_tpl.format(run_id=run_id)

    return os.path.join(state_dir, filename)

def init_checkpoint(checkpoint_path: str):
    if not os.path.exists(checkpoint_path):
        os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
        with open(checkpoint_path, "w", encoding="utf-8") as f:
            f.write("customer_id;status_global;processed_at\n")


def load_processed_ids(checkpoint_path: str) -> Set[str]:
    processed_ids: Set[str] = set()

    if not os.path.exists(checkpoint_path):
        return processed_ids

    with open(checkpoint_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            customer_id = row.get("customer_id")
            if customer_id:
                processed_ids.add(customer_id)

    return processed_ids

def append_checkpoint_row(checkpoint_path: str, customer_id: str, status: str):
    with open(checkpoint_path, "a", encoding="utf-8") as f:
        f.write(
            f"{customer_id};{status};{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )