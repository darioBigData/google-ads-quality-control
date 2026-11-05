def run(context: dict) -> dict:

    control_id = "AG005"

    try:

        assets = context.get("assets", [])

        EXPECTED_CTA = 2  # LEARN_MORE

        cta_assets = []

        for asset in assets:

            asset_type = asset.get("type")
            cta_value = asset.get("cta")

            if asset_type == "CALL_TO_ACTION_SELECTION" or cta_value is not None:
                cta_assets.append(asset)

        if not cta_assets:

            return {
                "control_id": control_id,
                "status": "SKIP",
                "valor_esperado": EXPECTED_CTA,
                "valor_encontrado": None,
                "detalle": "El Asset Group no contiene Call To Action",
                "error_tecnico": None
            }

        found_values = []

        for asset in cta_assets:

            value = asset.get("cta")

            if value is not None:
                found_values.append(value)

        if not found_values:

            return {
                "control_id": control_id,
                "status": "ERROR_TECNICO",
                "valor_esperado": EXPECTED_CTA,
                "valor_encontrado": None,
                "detalle": "Se detectó el asset CTA pero no su valor",
                "error_tecnico": "cta_value_missing"
            }

        for value in found_values:

            if value == EXPECTED_CTA:

                return {
                    "control_id": control_id,
                    "status": "OK",
                    "valor_esperado": EXPECTED_CTA,
                    "valor_encontrado": value,
                    "detalle": "El Call To Action es LEARN_MORE",
                    "error_tecnico": None
                }

        return {
            "control_id": control_id,
            "status": "ERROR",
            "valor_esperado": EXPECTED_CTA,
            "valor_encontrado": ", ".join(map(str, found_values)),
            "detalle": "El Call To Action no es LEARN_MORE",
            "error_tecnico": None
        }

    except Exception as e:

        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": None,
            "valor_encontrado": None,
            "detalle": "Error técnico durante la ejecución",
            "error_tecnico": str(e)
        }