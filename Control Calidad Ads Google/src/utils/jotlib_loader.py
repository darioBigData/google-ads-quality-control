import json
import os
import sys
from typing import Tuple


def ensure_jotlib_on_path(jotlib_path: str) -> None:
    """
    Añade jot_lib al sys.path si no está ya incluido.
    """

    if not jotlib_path:
        raise ValueError("jotlib_path no puede estar vacío.")

    if not os.path.isdir(jotlib_path):
        raise ValueError(f"jotlib_path no es una carpeta válida: {jotlib_path}")

    if jotlib_path not in sys.path:
        sys.path.insert(0, jotlib_path)


def load_google_ads_services(config_path: str) -> Tuple[object, object]:
    """
    Carga servicios de Google Ads usando jot_lib.
    """

    with open(config_path, "r", encoding="utf-8") as file:
        cfg = json.load(file)

    jotlib_path = cfg.get("jotlib_path", "").strip()
    if not jotlib_path:
        raise ValueError("config.json debe incluir 'jotlib_path'.")

    # Reutilizamos la función de bootstrap
    ensure_jotlib_on_path(jotlib_path)

    from jot.jot_googleads.auth import GoogleAdsAuth  # type: ignore
    from jot.jot_googleads.services.gaql import GAQLService  # type: ignore

    module_path = os.path.join(jotlib_path, "jot", "jot_googleads")
    auth = GoogleAdsAuth(module_path=module_path)
    client = auth.get_client()
    gaql = GAQLService(client)

    return client, gaql