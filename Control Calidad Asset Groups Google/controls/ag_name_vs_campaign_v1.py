import re

def normalize(text: str) -> str:
    """
    Normaliza strings para comparación flexible.
    """

    if not text:
        return ""

    text = text.lower()

    # quitar guiones y espacios
    text = text.replace("-", "")
    text = text.replace(" ", "")

    return text


def extract_keyword_block(campaign_name: str) -> str:
    """
    Extrae el bloque del nombre de campaña antes del (category_id)
    """

    if not campaign_name:
        return ""

    # Parte antes del category_id
    before_category = campaign_name.split("(")[0]

    # Nos quedamos con el último bloque separado por "_"
    parts = before_category.split("_")

    if not parts:
        return ""

    return parts[-1]


def run(context: dict) -> dict:

    
    control_id = "AG004"

    try:

        campaign = context.get("campaign", {})
        asset_group = context.get("asset_group", {})

        campaign_name = campaign.get("campaign_name")
        asset_group_name = asset_group.get("asset_group_name")

        if not campaign_name or not asset_group_name:

            return {
                "control_id": control_id,
                "status": "ERROR_TECNICO",
                "valor_esperado": None,
                "valor_encontrado": None,
                "detalle": "No se pudo obtener campaign_name o asset_group_name",
                "error_tecnico": "missing_campaign_or_asset_group_name"
            }

        expected_block = extract_keyword_block(campaign_name)

        if not expected_block:

            return {
                "control_id": control_id,
                "status": "ERROR_TECNICO",
                "valor_esperado": None,
                "valor_encontrado": None,
                "detalle": "No se pudo extraer el bloque del nombre de campaña",
                "error_tecnico": "campaign_block_not_found"
            }

        # Normalización para comparación
        normalized_campaign = normalize(expected_block)
        normalized_ag = normalize(asset_group_name)

        if normalized_campaign == normalized_ag:

            return {
                "control_id": control_id,
                "status": "OK",
                "valor_esperado": expected_block,
                "valor_encontrado": asset_group_name,
                "detalle": "El nombre del Asset Group coincide con el bloque de campaña",
                "error_tecnico": None
            }

        else:

            return {
                "control_id": control_id,
                "status": "ERROR",
                "valor_esperado": expected_block,
                "valor_encontrado": asset_group_name,
                "detalle": "El nombre del Asset Group no coincide con el bloque del nombre de campaña",
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