def run(context: dict, params: dict | None = None) -> dict:

    control_id = "2"
    print("--------------------------------------------------")
    print(f"[{control_id}]")

    try:
        campaign_type_raw = context.get("campaign", {}).get("campaign_type")
        ad_type_raw = context.get("ad", {}).get("type")

        campaign_type = str(campaign_type_raw or "").strip().upper()
        ad_type = str(ad_type_raw or "").strip().upper()

        EXPECTED_TYPES = {
            "SEARCH": "RESPONSIVE_SEARCH_AD",
            "DISPLAY": "RESPONSIVE_DISPLAY_AD"
        }

        print(f"[{control_id}] Campaign type raw:", campaign_type_raw)
        print(f"[{control_id}] Ad type raw:", ad_type_raw)
        print(f"[{control_id}] Campaign type normalized:", campaign_type)
        print(f"[{control_id}] Ad type normalized:", ad_type)
        print(f"[{control_id}] Expected mapping:", EXPECTED_TYPES)

        if campaign_type_raw is None:
            print(f"[{control_id}] ERROR_TECNICO - campaign_type missing")

            return _tech_error(control_id, "campaign_type_missing")

        if ad_type_raw is None:
            print(f"[{control_id}] ERROR_TECNICO - ad.type missing")

            return _tech_error(control_id, "ad_type_missing")

        if campaign_type not in EXPECTED_TYPES:
            print(f"[{control_id}] SKIP - unsupported campaign type")

            return {
                "control_id": control_id,
                "status": "SKIP",
                "valor_esperado": None,
                "valor_encontrado": campaign_type,
                "detalle": "Tipo de campaña no soportado",
                "error_tecnico": None
            }

        expected_type = EXPECTED_TYPES[campaign_type]

        print(f"[{control_id}] Expected type:", expected_type)

        if ad_type == "":
            print(f"[{control_id}] ERROR - empty ad type")

            return _error(control_id, expected_type, ad_type, "Tipo de anuncio vacío")

        if ad_type != expected_type:
            print(f"[{control_id}] ERROR - type mismatch")

            return _error(control_id, expected_type, ad_type, "Tipo de anuncio incorrecto")

        print(f"[{control_id}] OK - correct ad type")

        return {
            "control_id": control_id,
            "status": "OK",
            "valor_esperado": expected_type,
            "valor_encontrado": ad_type,
            "detalle": "Tipo correcto",
            "error_tecnico": None
        }

    except Exception as e:
        print(f"[{control_id}] ERROR_TECNICO:", str(e))

        return _tech_error(control_id, str(e))


def _error(control_id, esperado, encontrado, detalle):
    return {
        "control_id": control_id,
        "status": "ERROR",
        "valor_esperado": esperado,
        "valor_encontrado": encontrado,
        "detalle": detalle,
        "error_tecnico": None
    }


def _tech_error(control_id, error_msg):
    return {
        "control_id": control_id,
        "status": "ERROR_TECNICO",
        "valor_esperado": None,
        "valor_encontrado": None,
        "detalle": "Error técnico",
        "error_tecnico": error_msg
    }