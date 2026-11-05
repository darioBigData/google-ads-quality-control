import os


def get_checkpoint_path(run_id):
    return os.path.join("resume", f"checkpoint_{run_id}.log")


def load_checkpoint(run_id):

    path = get_checkpoint_path(run_id)

    processed = set()

    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                key = line.strip()
                if key:
                    processed.add(key)

    return {
        "processed_ids_set": processed,
        "path": path
    }


def add_processed_id(data, key):

    if key in data["processed_ids_set"]:
        return

    with open(data["path"], "a", encoding="utf-8") as f:
        f.write(key + "\n")

    data["processed_ids_set"].add(key)