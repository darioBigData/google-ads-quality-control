def run(context: dict) -> dict:

    control_id = "2"

    entity = context.get("entity", {})
    campaign_assets_count = context.get("campaign_assets_count", {})

    # =========================
    # VALIDACIÓN DE TIPO
    # =========================
    if entity.get("type") != "sitelink":
        return {
            "control_id": control_id,
            "status": "SKIP"
        }

    # =========================
    # OBTENER VALOR
    # =========================
    sitelinks_count = campaign_assets_count.get("sitelink", 0)

    # =========================
    # LÓGICA DE NEGOCIO
    # =========================
    if sitelinks_count >= 8:
        status = "OK"
        detalle = f"Sitelinks suficientes: {sitelinks_count}"

    else:
        status = "ERROR"
        detalle = f"Sitelinks insuficientes: {sitelinks_count} (< 8)"

    # =========================
    # RESULTADO
    # =========================
    return {
        "control_id": control_id,
        "status": status,
        "valor_esperado": ">= 8",
        "valor_encontrado": sitelinks_count,
        "detalle": detalle
    }