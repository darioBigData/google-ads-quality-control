from typing import Dict, List


REQUIRED_CONTROL_RESULT_FIELDS = [
    "control_id",
    "status",
    "valor_esperado",
    "valor_encontrado",
    "detalle",
    "error_tecnico"
]


def validate_input_headers(fieldnames: List[str]) -> None:
    required = {"customer_id"}
    available = set(fieldnames or [])

    missing = required - available
    if missing:
        raise ValueError(
            f"Faltan campos obligatorios en el input: {', '.join(sorted(missing))}"
        )

    allowed = {"customer_id", "campaign_id", "ad_group_id"}
    unexpected = available - allowed
    if unexpected:
        raise ValueError(
            "El input contiene campos no permitidos: "
            + ", ".join(sorted(unexpected))
        )


def validate_control_result(result: Dict) -> None:
    if not isinstance(result, dict):
        raise ValueError("El control debe devolver un dict.")

    missing = [field for field in REQUIRED_CONTROL_RESULT_FIELDS if field not in result]
    if missing:
        raise ValueError(
            "Faltan campos obligatorios en el resultado del control: "
            + ", ".join(missing)
        )

    allowed_statuses = {"OK", "ERROR", "SKIP", "ERROR_TECNICO"}
    if result["status"] not in allowed_statuses:
        raise ValueError(
            f"status inválido '{result['status']}'. "
            f"Valores permitidos: {sorted(allowed_statuses)}"
        )