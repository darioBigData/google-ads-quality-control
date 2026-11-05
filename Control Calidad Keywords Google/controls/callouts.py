def run(context: dict) -> dict:

    control_id = "3"

    entity = context.get("entity", {})
    campaign_assets_count = context.get("campaign_assets_count", {})

    # =========================
    # VALIDACIÓN DE TIPO
    # =========================
    if entity.get("type") != "callout":
        return {
            "control_id": control_id,
            "status": "SKIP"
        }

    # =========================
    # OBTENER VALOR
    # =========================
    callouts_count = campaign_assets_count.get("callout", 0)

    # =========================
    # LÓGICA DE NEGOCIO
    # =========================
    if callouts_count >= 6:
        status = "OK"
        detalle = f"Callouts suficientes: {callouts_count}"
    else:
        status = "ERROR"
        detalle = f"Callouts insuficientes: {callouts_count} (< 6)"

    # =========================
    # RESULTADO
    # =========================
    return {
        "control_id": control_id,
        "status": status,
        "valor_esperado": ">= 6",
        "valor_encontrado": callouts_count,
        "detalle": detalle
    }