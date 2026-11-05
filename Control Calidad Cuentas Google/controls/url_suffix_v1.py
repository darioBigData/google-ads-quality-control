def run(context: dict) -> dict:
    """
    Control 6 - Final URL Suffix (nivel cuenta)

    Regla de negocio:
    - El final_url_suffix debe estar vacío.
    - GAQL devuelve None cuando el campo no está informado.
    - Tanto None como "" se consideran CORRECTOS.
    """

    control_id = "6"

    account = context.get("account", {})
    final_url_suffix_real = account.get("final_url_suffix")

    # VALIDACIÓN FUNCIONAL - None o string vacío son válidos según negocio
    if final_url_suffix_real is None or final_url_suffix_real.strip() == "":
        return {
            "control_id": control_id,
            "status": "OK",
            "valor_esperado": "",
            "valor_encontrado": final_url_suffix_real,
            "detalle": "Final URL suffix vacio correctamente",
            "error_tecnico": None
        }

    # ERROR FUNCIONAL
    return {
        "control_id": control_id,
        "status": "ERROR",
        "valor_esperado": "",
        "valor_encontrado": final_url_suffix_real,
        "detalle": "Final URL suffix debe estar vacio",
        "error_tecnico": None
    }

