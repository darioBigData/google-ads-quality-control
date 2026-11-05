def run(context: dict, params: dict | None = None) -> dict:

    control_id = "3"

    try:
        ad = context.get("ad", {})
        business = context.get("business", {})
        catalogs = context.get("catalogs", {})

        ad_urls = ad.get("final_urls", [])

        destino = business.get("destino")
        pais = business.get("pais")
        idioma = business.get("idioma")

        urls_catalog = catalogs.get("urls_google", {})

        key = (destino, pais, idioma)
        valid_urls = urls_catalog.get(key, set())

        if not destino or not pais or not idioma:
            return _error(control_id, "Destino, país e idioma", str(key), "Datos incompletos")

        if not ad_urls:
            return _error(control_id, "Al menos una URL", "", "Sin URLs en anuncio")

        if not valid_urls:
            return _error(control_id, "Configuración en catálogo", "Vacío", "No hay URLs en catálogo")

        normalized_ad_urls = [_normalize_url(u) for u in ad_urls]
        normalized_valid_urls = {_normalize_url(u) for u in valid_urls}

        for url in normalized_ad_urls:
            if url in normalized_valid_urls:
                return {
                    "control_id": control_id,
                    "status": "OK",
                    "valor_esperado": "URL válida",
                    "valor_encontrado": url,
                    "detalle": "Coincidencia encontrada",
                    "error_tecnico": None
                }

        return _error(
            control_id,
            "Alguna URL válida",
            " | ".join(normalized_ad_urls),
            "No hay coincidencias"
        )

    except Exception as e:
        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": None,
            "valor_encontrado": None,
            "detalle": "Error inesperado",
            "error_tecnico": str(e)
        }


def _normalize_url(url: str) -> str:
    if not url:
        return ""
    return str(url).strip().lower()


def _error(control_id, esperado, encontrado, detalle):
    return {
        "control_id": control_id,
        "status": "ERROR",
        "valor_esperado": esperado,
        "valor_encontrado": encontrado,
        "detalle": detalle,
        "error_tecnico": None
    }