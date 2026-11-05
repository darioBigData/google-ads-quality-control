def run(context: dict) -> dict:

    control_id = "1"

    try:

        ad_group = context.get("ad_group", {}) or {}

        status = ad_group.get("status")
        ad_group_id = ad_group.get("ad_group_id")

        print(f"[DEBUG][C1] ad_group_id={ad_group_id} | status={status}")

        if status != "ENABLED":

            return {
                "control_id": control_id,
                "status": "ERROR",
                "valor_esperado": "ENABLED",
                "valor_encontrado": status,
                "detalle": f"Status incorrecto | DEBUG status={status}",
                "error_tecnico": None
            }

        return {
            "control_id": control_id,
            "status": "OK",
            "valor_esperado": "ENABLED",
            "valor_encontrado": status,
            "detalle": None,
            "error_tecnico": None
        }

    except Exception as e:

        print(f"[DEBUG][C1][ERROR] {e}")

        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": None,
            "valor_encontrado": None,
            "detalle": None,
            "error_tecnico": str(e)
        }