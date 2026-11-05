def run(context: dict) -> dict:
    """
    Control 8 – Content suitability (Dominios aparcados)

    Regla:
    La cuenta cumple si tiene excluida la categoría
    de contenido PARKED_DOMAIN a nivel cuenta.
    """

    control_id = "8"

    data = context["controls"].get("control_8", {})

    if data.get("error_tecnico") is not None:
        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": None,
            "valor_encontrado": None,
            "detalle": None,
            "error_tecnico": data["error_tecnico"],
        }

    rows = data.get("rows_returned")

    if rows is None:
        return {
            "control_id": control_id,
            "status": "ERROR",
            "valor_esperado": None,
            "valor_encontrado": None,
            "detalle": "NO_ROWS_INFO",
            "error_tecnico": None,
        }

    if rows > 0:
        return {
            "control_id": control_id,
            "status": "OK",
            "valor_esperado": "Parked domains excluidos",
            "valor_encontrado": "Excluidos",
            "detalle": None,
            "error_tecnico": None,
        }

    return {
        "control_id": control_id,
        "status": "ERROR",
        "valor_esperado": "Parked domains excluidos",
        "valor_encontrado": "No excluidos",
        "detalle": None,
        "error_tecnico": None,
    }
