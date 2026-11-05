def run(context: dict) -> dict:
    control_id = "7"

    try:
        # 1. Leer auto-tagging desde el contexto
        auto_tagging_enabled = context.get("account", {}).get("auto_tagging_enabled")

        if auto_tagging_enabled is None:
            return {
                "control_id": control_id,
                "status": "ERROR_TECNICO",
                "valor_esperado": "Auto-tagging activado",
                "valor_encontrado": None,
                "error_tecnico": "auto_tagging_enabled no disponible en el contexto"
            }

        # 2. Evaluación
        if auto_tagging_enabled is True:
            return {
                "control_id": control_id,
                "status": "OK",
                "valor_esperado": "Auto-tagging activado",
                "valor_encontrado": "Activado",
                "detalle": "El Auto Tagging esta activado para la cuenta",
                "error_tecnico": None
            }
        else:
            return {
                "control_id": control_id,
                "status": "ERROR",
                "valor_esperado": "Auto-tagging activado",
                "valor_encontrado": "Desactivado",
                "detalle": "El Auto Tagging esta desactivado para la cuenta",
                "error_tecnico": None
            }

    except Exception as e:
        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": "Auto-tagging activado",
            "valor_encontrado": None,
            "error_tecnico": str(e)
        }

