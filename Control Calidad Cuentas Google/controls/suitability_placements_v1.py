def run(context: dict) -> dict:
    """
    CONTROL 9 - EXCLUDED PLACEMENTS (ACCOUNT LEVEL)

    Valida que la cuenta tenga excluidos TODOS los emplazamientos requeridos
    a nivel cuenta, usando exclusivamente información precalculada
    en el context por el main.

    Este control:
    - NO ejecuta GAQL
    - NO ejecuta SQL
    - NO infiere estados
    - SOLO evalúa el context
    """

    control_id = "9"

    try:
        control_data = context["controls"].get("control_9")
        if not control_data:
            return {
                "control_id": control_id,
                "status": "ERROR_TECNICO",
                "valor_esperado": "Lista completa de emplazamientos excluidos",
                "valor_encontrado": None,
                "detalle": "CONTROL_9_CONTEXT_NO_PRESENTE",
                "error_tecnico": "No existe context['controls']['control_9']"
            }

        required_domains = control_data.get("required_domains", [])
        found_domains = control_data.get("found_domains", [])
        missing_domains = control_data.get("missing_domains", [])

        if missing_domains:
            return {
                "control_id": control_id,
                "status": "ERROR",
                "valor_esperado": f"{len(required_domains)} emplazamientos excluidos",
                "valor_encontrado": f"{len(found_domains)} emplazamientos excluidos",
                "detalle": f"FALTAN_EMP_EXCLUIDOS: {', '.join(missing_domains)}",
                "error_tecnico": None
            }

        return {
            "control_id": control_id,
            "status": "OK",
            "valor_esperado": f"{len(required_domains)} emplazamientos excluidos",
            "valor_encontrado": f"{len(found_domains)} emplazamientos excluidos",
            "detalle": "TODOS_LOS_EMP_REQUERIDOS_ESTAN_EXCLUIDOS",
            "error_tecnico": None
        }

    except Exception as e:
        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": None,
            "valor_encontrado": None,
            "detalle": "EXCEPCION_NO_CONTROLADA",
            "error_tecnico": str(e)
        }
