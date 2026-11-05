def run(context: dict) -> dict:

    control_id = "5"

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
    match_type = raw.get("match_type")

    # =========================
    # LÓGICA DE NEGOCIO
    # =========================
    if not match_type:
        status = "ERROR"
        detalle = "Match type no informado"
    elif match_type == "BROAD":
        status = "OK"
        detalle = f"Match type correcto: {match_type}"
    else:
        status = "ERROR"
        detalle = f"Match type incorrecto: {match_type}"

    # =========================
    # RESULTADO
    # =========================
    return {
        "control_id": control_id,
        "status": status,
        "valor_esperado": "BROAD",
        "valor_encontrado": match_type,
        "detalle": detalle
    }