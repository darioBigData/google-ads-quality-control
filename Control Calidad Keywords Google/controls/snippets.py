def run(context: dict) -> dict:

    control_id = "4"

    entity = context.get("entity", {})
    campaign_assets_count = context.get("campaign_assets_count", {})

    # =========================
    # VALIDACIÓN DE TIPO
    # =========================
    if entity.get("type") != "snippet":
        return {
            "control_id": control_id,
            "status": "SKIP"
        }

    # =========================
    # OBTENER VALOR
    # =========================
    snippets_count = campaign_assets_count.get("snippet", 0)

    # =========================
    # LÓGICA DE NEGOCIO
    # =========================
    if snippets_count >= 1:
        status = "OK"
        detalle = f"Snippets suficientes: {snippets_count}"
    else:
        status = "ERROR"
        detalle = f"Snippets insuficientes: {snippets_count} (< 1)"

    # =========================
    # RESULTADO
    # =========================
    return {
        "control_id": control_id,
        "status": status,
        "valor_esperado": ">= 1",
        "valor_encontrado": snippets_count,
        "detalle": detalle
    }