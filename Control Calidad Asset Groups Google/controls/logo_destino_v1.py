from core.context_utils import (
    get_account_destino,
    contains_ignore_case,
    safe_join_for_output
)


def run(context: dict) -> dict:

    control_id = "AG007"

    try:

        logos = context.get("logos", [])
        destino = get_account_destino(context)

        if not destino:

            return {
                "control_id": control_id,
                "status": "ERROR_TECNICO",
                "valor_esperado": "Destino disponible en cuenta",
                "valor_encontrado": None,
                "detalle": "No se pudo obtener destino",
                "error_tecnico": "account.destino missing"
            }

        if not logos:

            return {
                "control_id": control_id,
                "status": "SKIP",
                "valor_esperado": f"Logotipos con iniciales {destino}",
                "valor_encontrado": 0,
                "detalle": "Asset group sin logotipos",
                "error_tecnico": None
            }

        invalid_logos = []

        for logo in logos:

            asset_name = logo.get("name")

            if not contains_ignore_case(asset_name, destino):

                invalid_logos.append(asset_name)

        if invalid_logos:

            return {
                "control_id": control_id,
                "status": "ERROR",
                "valor_esperado": destino,
                "valor_encontrado": safe_join_for_output(invalid_logos),
                "detalle": "Logotipos con destino incorrecto",
                "error_tecnico": None
            }

        return {
            "control_id": control_id,
            "status": "OK",
            "valor_esperado": destino,
            "valor_encontrado": destino,
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