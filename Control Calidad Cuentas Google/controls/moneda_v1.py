def run(context: dict) -> dict:
    control_id = "4"
    nombre_control = "Moneda"

    # Valor esperado
    valor_esperado = "HKD"

    try:
        valor_encontrado = context.get("account", {}).get("currency")

        if not valor_encontrado:
            status = "ERROR"
        else:
            if valor_encontrado.strip().upper() == valor_esperado:
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
