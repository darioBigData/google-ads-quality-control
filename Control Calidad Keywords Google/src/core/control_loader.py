import json
import importlib.util
import os


def load_controls(path):

    with open(path, "r", encoding="utf-8") as f:
        controls_def = json.load(f)

    controls = []

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    for c in controls_def:

        script_path = os.path.join(base_dir, c["control_script"])

        spec = importlib.util.spec_from_file_location(
            f"control_{c['control_id']}",
            script_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        controls.append({
            "control_id": c["control_id"],
            "control_name": c["control_name"],
            "entity_type": c["entity_type"],
            "run": module.run
        })

    return controls