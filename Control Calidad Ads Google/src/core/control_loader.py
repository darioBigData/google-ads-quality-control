import importlib.util
import json
import os
from typing import Dict, List


def load_controls(controls_file: str) -> List[Dict]:
    with open(controls_file, "r", encoding="utf-8") as file:
        raw_controls = json.load(file)

    controls = []
    for item in raw_controls:
        if not item.get("enabled", True):
            continue

        module = _load_module_from_path(item["control_script"])
        controls.append({
            "control_id": item["control_id"],
            "control_name": item["control_name"],
            "params": item.get("params", {}),
            "run": module.run
        })

    return controls


def _load_module_from_path(module_path: str):
    absolute_path = os.path.abspath(module_path)
    if not os.path.exists(absolute_path):
        raise FileNotFoundError(f"No existe el control: {absolute_path}")

    module_name = os.path.splitext(os.path.basename(absolute_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, absolute_path)
    module = importlib.util.module_from_spec(spec)

    if spec is None or spec.loader is None:
        raise ImportError(f"No se pudo cargar el módulo: {module_path}")

    spec.loader.exec_module(module)
    return module