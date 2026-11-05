def run(context: dict) -> dict:

    control_id = "1"

    entity = context.get("entity", {})
    raw = entity.get("raw", {})

    # =========================
    # VALIDACIÓN DE TIPO
    # =========================
    if entity.get("type") != "keyword":
        return {
            "control_id": control_id,
            "status": "SKIP"
        }

    # =========================
    # OBTENER VALOR
    # =========================
    approval_status = raw.get("approval_status")

    # =========================
    # LÓGICA DE NEGOCIO
    # =========================
    if not approval_status:
        status = "ERROR"
        detalle = "Approval status no informado"

    elif approval_status == "DISAPPROVED":
        status = "ERROR"
        detalle = "Keyword rechazada"

    else:
        status = "OK"
        detalle = f"Keyword aprobada: {approval_status}"

    # =========================
    # RESULTADO
    # =========================
    return {
        "control_id": control_id,
        "status": status,
        "valor_esperado": "No DISAPPROVED",
        "valor_encontrado": approval_status,
        "detalle": detalle
    }