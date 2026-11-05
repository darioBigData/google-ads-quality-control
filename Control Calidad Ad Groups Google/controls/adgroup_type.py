def run(context: dict) -> dict:

    control_id = "2"

    try:

        ad_group = context.get("ad_group", {}) or {}

        ag_type = ad_group.get("type")
        ad_group_id = ad_group.get("ad_group_id")

        print(f"[DEBUG][C2] ad_group_id={ad_group_id} | type={ag_type}")

        if ag_type != "STANDARD":

            return {
                "control_id": control_id,
                "status": "ERROR",
                "valor_esperado": "STANDARD",
                "valor_encontrado": ag_type,
                "detalle": f"Tipo incorrecto | DEBUG type={ag_type}",
                "error_tecnico": None
            }

        return {
            "control_id": control_id,
            "status": "OK",
            "valor_esperado": "STANDARD",
            "valor_encontrado": ag_type,
            "detalle": None,
            "error_tecnico": None
        }

    except Exception as e:

        print(f"[DEBUG][C2][ERROR] {e}")

        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": None,
            "valor_encontrado": None,
            "detalle": None,
            "error_tecnico": str(e)
        }