def validate_control_result(result: dict):

    if not isinstance(result, dict):
        raise ValueError("El resultado del control debe ser un diccionario")

    required_fields = [
        "control_id",
        "status"
    ]

    for field in required_fields:
        if field not in result:
            raise ValueError(f"Falta campo obligatorio en control result: {field}")

    valid_status = {"OK", "ERROR", "SKIP", "ERROR_TECNICO"}

    if result["status"] not in valid_status:
        raise ValueError(
            f"Status inválido en control {result.get('control_id')}: {result['status']}"
        )

    # Campos opcionales pero recomendados
    optional_fields = [
        "valor_esperado",
        "valor_encontrado",
        "detalle"
    ]

    for field in optional_fields:
        if field not in result:
            result[field] = None

    return result