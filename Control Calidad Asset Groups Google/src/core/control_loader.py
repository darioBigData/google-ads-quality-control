import importlib.util
import os


def load_control(control_script):

    root_path = os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__)
        )
    )

    script_path = os.path.join(
        root_path,
        control_script
    )

    if not os.path.exists(script_path):
        raise FileNotFoundError(
            f"Control no encontrado: {script_path}"
        )

    module_name = os.path.basename(script_path).replace(".py", "")

    spec = importlib.util.spec_from_file_location(
        module_name,
        script_path
    )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module