import os
import json

# ---------------------------------------------------------
# CHECKPOINT DIRECTORY
# ---------------------------------------------------------
def get_checkpoint_dir():

    base_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )

    checkpoint_dir = os.path.join(
        base_dir,
        "checkpoints"
    )

    os.makedirs(checkpoint_dir, exist_ok=True)

    return checkpoint_dir


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------
def get_checkpoint_paths(run_id):

    checkpoint_dir = get_checkpoint_dir()

    meta_path = os.path.join(
        checkpoint_dir,
        f"checkpoint_ag_{run_id}.meta.json"
    )

    log_path = os.path.join(
        checkpoint_dir,
        f"checkpoint_ag_{run_id}.done.log"
    )

    return meta_path, log_path


# ---------------------------------------------------------
# LOAD CHECKPOINT
# ---------------------------------------------------------
def load_checkpoint(run_id):

    meta_path, log_path = get_checkpoint_paths(run_id)

    processed_ids_set = set()

    # ---- LOAD LOG (append-only) ----
    if os.path.isfile(log_path):

        with open(log_path, "r", encoding="utf-8") as f:

            for line in f:

                key = line.strip()

                if key:
                    processed_ids_set.add(key)

    # ---- LOAD META (optional) ----
    meta = {}

    if os.path.isfile(meta_path):

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            meta = {}

    return {
        "processed_ids_set": processed_ids_set,
        "meta": meta,
        "log_path": log_path,
        "meta_path": meta_path
    }


# ---------------------------------------------------------
# SAVE META (LIGHTWEIGHT)
# ---------------------------------------------------------
def save_meta(meta_path, meta_data):

    tmp_path = meta_path + ".tmp"

    with open(tmp_path, "w", encoding="utf-8") as f:

        json.dump(
            meta_data,
            f,
            separators=(",", ":")  # compacto
        )

        f.flush()
        os.fsync(f.fileno())

    os.replace(tmp_path, meta_path)


# ---------------------------------------------------------
# ADD PROCESSED ID (APPEND-ONLY)
# ---------------------------------------------------------
def add_processed_id(checkpoint_data, checkpoint_key):

    processed_ids_set = checkpoint_data["processed_ids_set"]
    log_path = checkpoint_data["log_path"]

    if checkpoint_key in processed_ids_set:
        return

    # ---- APPEND ----
    with open(log_path, "a", encoding="utf-8") as f:

        f.write(checkpoint_key + "\n")
        f.flush()
        os.fsync(f.fileno())

    processed_ids_set.add(checkpoint_key)