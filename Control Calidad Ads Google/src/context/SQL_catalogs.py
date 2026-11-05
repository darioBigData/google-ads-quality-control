"""
SQL Catalogs - QC Ads

Módulo centralizado para carga de catálogos SQL.

Responsabilidades:
- Cargar catálogos desde SQL Server.
- Normalizar datos.
- Preparar estructuras optimizadas para lookup O(1).
- NO aplicar reglas de negocio.
- NO depender del context.
"""


# --- URLS GOOGLE ADS ---
def load_urls_google(sql) -> dict:
    """
    Catálogo de URLs Google Ads.

    Clave:
        (destino_codigo, pais_jot, idioma)

    Valor:
        set(urls)

    Fuente:
        [Jot_admin].[dbo].[tbl_Checklist_Codigos]
    """

    query = """
    SELECT
        RTRIM(LTRIM(Destino_Codigo)) AS Destino_Codigo,
        RTRIM(LTRIM(Pais_Jot))       AS Pais_Jot,
        RTRIM(LTRIM(Idioma))         AS Idioma,
        RTRIM(LTRIM(URL))            AS URL
    FROM [Jot_admin].[dbo].[tbl_Checklist_Codigos]
    WHERE Plataforma = 'Google'
      AND Partner = 'VSM'
    """

    rows = sql.run_query(query)

    urls_catalog = {}

    for row in rows:

        if not row or len(row) < 4:
            continue

        destino_codigo = (row[0] or "").strip().upper()
        pais_jot = (row[1] or "").strip().upper()
        idioma = (row[2] or "").strip().upper()
        url = (row[3] or "").strip()

        if not (destino_codigo and pais_jot and idioma and url):
            continue

        key = (destino_codigo, pais_jot, idioma)

        if key not in urls_catalog:
            urls_catalog[key] = set()

        urls_catalog[key].add(url)

    return urls_catalog


# --- VALIDACIÓN BÁSICA ---
def _validate_urls_catalog(urls_catalog: dict):
    """
    Validación estructural básica del catálogo de URLs.
    """

    if not isinstance(urls_catalog, dict):
        raise Exception("CATALOG_ERROR: urls_catalog no es un dict")

    for key, urls in urls_catalog.items():

        if not isinstance(key, tuple) or len(key) != 3:
            raise Exception(f"CATALOG_ERROR: key inválida {key}")

        if not isinstance(urls, set):
            raise Exception(f"CATALOG_ERROR: urls no es set para {key}")

        if not urls:
            raise Exception(f"CATALOG_ERROR: conjunto vacío para {key}")


# --- ORQUESTADOR ---
def load_all_catalogs(sql) -> dict:
    """
    Carga todos los catálogos necesarios para el QC de Ads.
    """

    catalogs = {}

    # URLS
    urls_catalog = load_urls_google(sql)

    _validate_urls_catalog(urls_catalog)

    catalogs["urls_google"] = urls_catalog

    return catalogs