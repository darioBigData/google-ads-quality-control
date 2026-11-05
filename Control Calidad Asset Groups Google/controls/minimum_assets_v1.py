from core.context_utils import safe_join_for_output


def run(context: dict) -> dict:

    control_id = "AG001"

    try:

        asset_counts = context.get("asset_counts", {})

        if asset_counts is None:

            return {
                "control_id": control_id,
                "status": "ERROR_TECNICO",
                "valor_esperado": "asset_counts disponible en contexto",
                "valor_encontrado": None,
                "detalle": "No se pudo obtener asset_counts",
                "error_tecnico": "context['asset_counts'] missing"
            }

        min_requirements = {
            "HEADLINE": 5,
            "LONG_HEADLINE": 1,
            "DESCRIPTION": 2
        }

        missing_assets = []

        for asset_type, minimum in min_requirements.items():

            current_count = asset_counts.get(asset_type, 0)

            if current_count < minimum:

                missing_assets.append(
                    f"{asset_type}:{current_count}/{minimum}"
                )

        if missing_assets:

            return {
                "control_id": control_id,
                "status": "ERROR",
                "valor_esperado": safe_join_for_output(
                    [f"{k}>={v}" for k, v in min_requirements.items()]
                ),
                "valor_encontrado": safe_join_for_output(missing_assets),
                "detalle": "Asset Group no cumple mínimos de assets",
                "error_tecnico": None
            }

        return {
            "control_id": control_id,
            "status": "OK",
            "valor_esperado": safe_join_for_output(
                [f"{k}>={v}" for k, v in min_requirements.items()]
            ),
            "valor_encontrado": safe_join_for_output(
                [f"{k}:{asset_counts.get(k,0)}" for k in min_requirements]
            ),
            "detalle": None,
            "error_tecnico": None
        }

    except Exception as e:

        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": None,
            "valor_encontrado": None,
            "detalle": None,
            "error_tecnico": str(e)
        }