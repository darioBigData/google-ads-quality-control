def _path_exists(data: dict, path: str) -> bool:
    """
    Comprueba si una ruta tipo 'a.b.c' existe en un dict anidado
    """
    current = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return True


CONTROL_CONTEXT_REQUIREMENTS = {
    # Control 2 — Línea de negocio
    "2": [
        "input.customer_id",
        "services.google_ads",
        "account.linea_negocio",
    ],

    # Control 5 — Tracking template
    "5": [
        "account.socio",
        "account.canal_compra",
        "account.tipo_landing",
        "account.tracking_template",
        "tracking_catalog"
    ],

    # Control 8 — Parked domains
    "8": [
        "controls.control_8.rows_returned",
    ],

    # Control 9 — Excluded placements
    "9": [
        "controls.control_9.required_domains",
        "controls.control_9.found_domains",
    ],
}


def validate_context_for_control(context: dict, control_id: str) -> list[str]:
    """
    Devuelve la lista de paths que faltan para un control.
    Si está vacía → contexto válido.
    """
    required_paths = CONTROL_CONTEXT_REQUIREMENTS.get(control_id, [])
    missing = []

    for path in required_paths:
        if not _path_exists(context, path):
            missing.append(path)

    return missing
