def run(context: dict) -> dict:
    control_id = "3"
    nombre_control = "Zona horaria"

    """
    Valor esperado para todas las cuentas:
    # UI: (GMT-08:00 1 Nov - 7 Marzo / GMT-08:00 8 Marzo - 31 Oct) hora del Pacífico
    # API: America/Los_Angeles
    """
    valor_esperado = "America/Los_Angeles"
    
    try:
        valor_encontrado = context.get("account", {}).get("timezone")

        if not valor_encontrado:
            status = "ERROR"
        else:
            if valor_encontrado.strip() == valor_esperado:
                status = "OK"
            else:
                status = "ERROR"

        return {
            "control_id": control_id,
            "nombre_control": nombre_control,
            "status": status,
            "valor_esperado": valor_esperado,
            "valor_encontrado": valor_encontrado,
            "error_tecnico": None
        }

    except Exception as e:
        return {
            "control_id": control_id,
            "nombre_control": nombre_control,
            "status": "ERROR_TECNICO",
            "valor_esperado": valor_esperado,
            "valor_encontrado": None,
            "error_tecnico": str(e)
        }

