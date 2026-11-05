def run(context: dict) -> dict:

    control_id = "3"

    try:

        ad_group = context.get("ad_group", {}) or {}

        bid_modifiers = ad_group.get("bid_modifiers", []) or []
        ad_group_id = ad_group.get("ad_group_id")

        print(f"[DEBUG][C3] ad_group_id={ad_group_id} | bid_modifiers={bid_modifiers}")

        # 🔥 SOLO error si existe ajuste a nivel AD_GROUP
        has_adgroup_modifier = "AD_GROUP" in bid_modifiers

        if has_adgroup_modifier:

            return {
                "control_id": control_id,
                "status": "ERROR",
                "valor_esperado": "Sin bid modifiers a nivel AD_GROUP",
                "valor_encontrado": bid_modifiers,
                "detalle": f"Bid modifier a nivel AD_GROUP detectado | DEBUG={bid_modifiers}",
                "error_tecnico": None
            }

        return {
            "control_id": control_id,
            "status": "OK",
            "valor_esperado": "Sin bid modifiers a nivel AD_GROUP",
            "valor_encontrado": bid_modifiers,
            "detalle": None,
            "error_tecnico": None
        }

    except Exception as e:

        print(f"[DEBUG][C3][ERROR] {e}")

        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": None,
            "valor_encontrado": None,
            "detalle": None,
            "error_tecnico": str(e)
        }