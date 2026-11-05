def run(context: dict, params: dict | None = None) -> dict:

    control_id = "1"
    print("--------------------------------------------------")
    print(f"[{control_id}]")

    try:
        params = params or {}
        allowed_statuses = set(params.get("allowed_statuses", ["ENABLED", "REMOVED"]))

        raw_status = context.get("ad", {}).get("status")
        found_status = (raw_status or "").strip().upper()

        print(f"[{control_id}] Raw status:", raw_status)
        print(f"[{control_id}] Normalized status:", found_status)
        print(f"[{control_id}] Allowed statuses:", allowed_statuses)

        if raw_status is None:
            print(f"[{control_id}] ERROR_TECNICO - ad_status missing")

            return {
                "control_id": control_id,
                "status": "ERROR_TECNICO",
                "valor_esperado": None,
                "valor_encontrado": None,
                "detalle": "Falta 'ad_status' en el contexto",
                "error_tecnico": "ad_status_missing"
            }

        if found_status == "":
            print(f"[{control_id}] ERROR - empty status")

            return _error(control_id, "Estado informado", "", "El anuncio no tiene estado")

        if found_status not in allowed_statuses:
            print(f"[{control_id}] ERROR - invalid status")

            return _error(
                control_id,
                f"Estados permitidos: {', '.join(sorted(allowed_statuses))}",
                found_status,
                "Estado no permitido"
            )

        print(f"[{control_id}] OK - valid status")

        return {
            "control_id": control_id,
            "status": "OK",
            "valor_esperado": ", ".join(sorted(allowed_statuses)),
            "valor_encontrado": found_status,
            "detalle": "Estado correcto",
            "error_tecnico": None
        }

    except Exception as e:
        print(f"[{control_id}] ERROR_TECNICO:", str(e))

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