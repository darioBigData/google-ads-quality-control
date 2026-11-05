def run(context: dict, params: dict | None = None) -> dict:

    control_id = "1"

    try:
        params = params or {}
        allowed_statuses = set(params.get("allowed_statuses", ["ENABLED", "REMOVED"]))

        raw_status = context.get("ad", {}).get("status")
        found_status = (raw_status or "").strip().upper()

        if raw_status is None:
            return {
                "control_id": control_id,
                "status": "ERROR_TECNICO",
                "valor_esperado": None,
                "valor_encontrado": None,
                "detalle": "Falta 'ad_status' en el contexto",
                "error_tecnico": "ad_status_missing"
            }

        if found_status == "":
            return _error(control_id, "Estado informado", "", "El anuncio no tiene estado")

        if found_status not in allowed_statuses:
            return _error(
                control_id,
                f"Estados permitidos: {', '.join(sorted(allowed_statuses))}",
                found_status,
                "Estado no permitido"
            )

        return {
            "control_id": control_id,
            "status": "OK",
            "valor_esperado": ", ".join(sorted(allowed_statuses)),
            "valor_encontrado": found_status,
            "detalle": "Estado correcto",
            "error_tecnico": None
        }

    except Exception as e:
        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": None,
            "valor_encontrado": None,
            "detalle": "Error inesperado",
            "error_tecnico": str(e)
        }


def _error(control_id, esperado, encontrado, detalle):
    return {
        "control_id": control_id,
        "status": "ERROR",
        "valor_esperado": esperado,
        "valor_encontrado": encontrado,
        "detalle": detalle,
        "error_tecnico": None
    }