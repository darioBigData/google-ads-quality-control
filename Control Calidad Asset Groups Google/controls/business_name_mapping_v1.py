EXPECTED_MAPPING = {
    "BKV": "Blinkvox",
    "CIF": "Calminform",
    "EDU": "Edufindly",
    "IGN": "Ignaly",
    "SEK": "Seek And Ye Shall Find",
    "DSR": "Discovery Searcher",
    "BES": "Best Entertainment Spot",
    "FQQ": "Fast Query Quest",
    "FAE": "Fast Answer Explore",
    "MSP": "Mindspark",
    "IQI": "Inquiry Insider",
    "ASF": "Answers Fetcher"
}


def run(context: dict) -> dict:

    control_id = "AG003"

    try:

        account = context.get("account", {})
        assets = context.get("assets", [])

        destino = account.get("destino")

        if not destino:
            print(f"[{control_id}] ERROR_TECNICO - destino not available")

            return {
                "control_id": control_id,
                "status": "ERROR_TECNICO",
                "valor_esperado": None,
                "valor_encontrado": None,
                "detalle": "No se pudo obtener el destino de la cuenta",
                "error_tecnico": "destino_missing"
            }

        expected_value = EXPECTED_MAPPING.get(destino)

        if not expected_value:
            print(f"[{control_id}] ERROR_TECNICO - destino not mapped")

            return {
                "control_id": control_id,
                "status": "ERROR_TECNICO",
                "valor_esperado": None,
                "valor_encontrado": None,
                "detalle": f"No existe mapping definido para destino: {destino}",
                "error_tecnico": "destino_mapping_missing"
            }

        # --- Buscar BUSINESS_NAME assets ---
        business_assets = []

        for asset in assets:

            asset_type = asset.get("asset_type") or asset.get("type")

            if asset_type == "BUSINESS_NAME":
                business_assets.append(asset)

        # --- Caso SKIP ---
        if not business_assets:

            return {
                "control_id": control_id,
                "status": "SKIP",
                "valor_esperado": expected_value,
                "valor_encontrado": None,
                "detalle": "El Asset Group no contiene BUSINESS_NAME",
                "error_tecnico": None
            }

        # --- Extraer valores encontrados ---
        found_values = []

        for asset in business_assets:

            value = asset.get("text")

            if value:
                found_values.append(value.strip())

        # --- Validación ---
        for value in found_values:

            if value == expected_value:

                return {
                    "control_id": control_id,
                    "status": "OK",
                    "valor_esperado": expected_value,
                    "valor_encontrado": value,
                    "detalle": "BUSINESS_NAME correcto",
                    "error_tecnico": None
                }

        # --- ERROR si ninguno coincide ---
        return {
            "control_id": control_id,
            "status": "ERROR",
            "valor_esperado": expected_value,
            "valor_encontrado": ", ".join(found_values),
            "detalle": "El BUSINESS_NAME no coincide con el esperado para el destino",
            "error_tecnico": None
        }

    except Exception as e:

        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": None,
            "valor_encontrado": None,
            "detalle": "Error técnico durante la ejecución del control",
            "error_tecnico": str(e)
        }