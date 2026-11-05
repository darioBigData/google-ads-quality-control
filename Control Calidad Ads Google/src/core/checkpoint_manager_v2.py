import json
import os
from typing import Set


class CheckpointManager:
    def __init__(self, checkpoint_file: str):
        self.checkpoint_file = checkpoint_file
        self.data = {
            "processed_keys": []
        }

        os.makedirs(os.path.dirname(self.checkpoint_file), exist_ok=True)

        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, "r", encoding="utf-8") as file:
                self.data = json.load(file)

    def save(self) -> None:
        with open(self.checkpoint_file, "w", encoding="utf-8") as file:
            json.dump(self.data, file, ensure_ascii=False, indent=2)

    def has_processed(self, ad_key: str) -> bool:
        return ad_key in set(self.data.get("processed_keys", []))

    def mark_processed(self, ad_key: str) -> None:
        processed: Set[str] = set(self.data.get("processed_keys", []))
        processed.add(ad_key)
        self.data["processed_keys"] = sorted(processed)
        self.save()

    def get_processed_count(self) -> int:
        return len(self.data.get("processed_keys", []))

    def delete(self) -> None:
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)