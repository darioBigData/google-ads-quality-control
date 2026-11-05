def run(context: dict) -> dict:

    control_id = "4"

    try:

        ad_group = context.get("ad_group", {}) or {}

        cpc_micros = ad_group.get("cpc_bid_micros")
        ad_group_id = ad_group.get("ad_group_id")

        euros = None
        if cpc_micros is not None:
            euros = cpc_micros / 1_000_000

        print(f"[DEBUG][C4] ad_group_id={ad_group_id} | micros={cpc_micros} | euros={euros}")

        expected = 10000

        if cpc_micros != expected:

            return {
                "control_id": control_id,
                "status": "ERROR",
                "valor_esperado": expected,
                "valor_encontrado": cpc_micros,
                "detalle": f"CPC incorrecto | DEBUG euros={euros}",
                "error_tecnico": None
            }

        return {
            "control_id": control_id,
            "status": "OK",
            "valor_esperado": expected,
            "valor_encontrado": cpc_micros,
            "detalle": None,
            "error_tecnico": None
        }

    except Exception as e:

        print(f"[DEBUG][C4][ERROR] {e}")

        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": None,
            "valor_encontrado": None,
            "detalle": None,
            "error_tecnico": str(e)
        }