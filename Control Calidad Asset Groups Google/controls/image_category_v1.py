from core.context_utils import (
    get_campaign_category_id,
    extract_category_id_from_asset_name,
    safe_join_for_output
)


def run(context: dict) -> dict:

    control_id = "AG006"

    try:

        images = context.get("images", [])
        campaign_category = get_campaign_category_id(context)

        if not campaign_category:

            return {
                "control_id": control_id,
                "status": "ERROR_TECNICO",
                "valor_esperado": "Category ID disponible en campaña",
                "valor_encontrado": None,
                "detalle": "No se pudo extraer category_id",
                "error_tecnico": "campaign.category_id missing"
            }

        if not images:

            return {
                "control_id": control_id,
                "status": "SKIP",
                "valor_esperado": f"Imágenes con category_id {campaign_category}",
                "valor_encontrado": 0,
                "detalle": "Asset group sin imágenes",
                "error_tecnico": None
            }

        valid_images = []
        generic_images = []
        invalid_images = []

        for image in images:

            name = image.get("name")

            if not name:
                continue

            extracted_category = extract_category_id_from_asset_name(name)

            if extracted_category is None:
                generic_images.append(name)

            elif extracted_category == campaign_category:
                valid_images.append(name)

            else:
                invalid_images.append(name)

        # --- ERROR: hay imágenes con category_id incorrecto ---
        if invalid_images:

            return {
                "control_id": control_id,
                "status": "ERROR",
                "valor_esperado": campaign_category,
                "valor_encontrado": safe_join_for_output(invalid_images),
                "detalle": "Imágenes con categoría incorrecta",
                "error_tecnico": None
            }

        # --- ERROR: no hay ninguna imagen categórica válida ---
        if not valid_images:

            return {
                "control_id": control_id,
                "status": "ERROR",
                "valor_esperado": campaign_category,
                "valor_encontrado": safe_join_for_output(generic_images),
                "detalle": "No existen imágenes con category_id de la campaña",
                "error_tecnico": None
            }

        # --- OK ---
        return {
            "control_id": control_id,
            "status": "OK",
            "valor_esperado": campaign_category,
            "valor_encontrado": campaign_category,
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