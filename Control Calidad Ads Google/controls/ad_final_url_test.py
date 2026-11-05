def run(context: dict, params: dict | None = None) -> dict:

    control_id = "3"
    print("--------------------------------------------------")
    print(f"[{control_id}]")

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

        print(f"[{control_id}] Business key:", key)
        print(f"[{control_id}] Ad URLs:", ad_urls)
        print(f"[{control_id}] Catalog URLs:", valid_urls)

        if not destino or not pais or not idioma:
            print(f"[{control_id}] ERROR - missing business data")

            return _error(control_id, "Destino, país e idioma", str(key), "Datos incompletos")

        if not ad_urls:
            print(f"[{control_id}] ERROR - no URLs in ad")

            return _error(control_id, "Al menos una URL", "", "Sin URLs en anuncio")

        if not valid_urls:
            print(f"[{control_id}] ERROR - no catalog URLs")

            return _error(control_id, "Configuración en catálogo", "Vacío", "No hay URLs en catálogo")

        normalized_ad_urls = [_normalize_url(u) for u in ad_urls]
        normalized_valid_urls = {_normalize_url(u) for u in valid_urls}

        print(f"[{control_id}] Normalized ad URLs:", normalized_ad_urls)
        print(f"[{control_id}] Normalized catalog URLs:", normalized_valid_urls)

        for url in normalized_ad_urls:
            if url in normalized_valid_urls:
                print(f"[{control_id}] OK - matching URL found")

                return {
                    "control_id": control_id,
                    "status": "OK",
                    "valor_esperado": "URL válida",
                    "valor_encontrado": url,
                    "detalle": "Coincidencia encontrada",
                    "error_tecnico": None
                }

        print(f"[{control_id}] ERROR - no matching URLs")

        return _error(
            control_id,
            "Alguna URL válida",
            " | ".join(normalized_ad_urls),
            "No hay coincidencias"
        )

    except Exception as e:
        print(f"[{control_id}] ERROR_TECNICO:", str(e))

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