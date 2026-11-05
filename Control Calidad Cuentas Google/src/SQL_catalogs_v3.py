def load_sql_catalogs(sql) -> dict:
    """
    Carga catálogos estáticos desde SQL Server desde la BBDD jot_admin una sola vez por ejecución.

    Devuelve un diccionario listo para lookup O(1) en controles.

    Esta función:
    - NO aplica reglas de negocio
    - NO depende de cuentas
    - NO modifica el context
    - SOLO carga y normaliza datos
    """

    catalogs = {
        "socios": set(),
        "destinos": set(),
        "paises": set(),
        "dispositivos": set(),
        "config_geo_by_ln_key": {},
        "destinos_by_socio_id": {},
        "excluded_placements_control_9": set()
    }

    # --- SOCIOS ---
    query_socios = """
    SELECT RTRIM(LTRIM(Socio_codigo)) AS codigo
    FROM dimensiones.tbl_Socios
    """
    for row in sql.run_query(query_socios):
        codigo = row[0]
        if codigo:
            catalogs["socios"].add(codigo.strip().upper())

    # --- DESTINOS ---
    query_destinos = """
    SELECT
        RTRIM(LTRIM(Destino_codigo)),
        CAST(Socio_id AS VARCHAR(10)),
        Es_activo
    FROM dimensiones.tbl_Destinos
    WHERE Socio_id = 25
      AND Es_activo = 1
    """
    # Catálogo plano de destinos existentes
    catalogs.setdefault("destinos", set())

    # Catálogo derivado: destinos activos por socio (Control 1 - coherencia socio/destino)
    catalogs.setdefault("destinos_by_socio_id", {})

    for row in sql.run_query(query_destinos):
        if not row or not row[0] or not row[1]:
            continue

        destino = row[0].strip().upper()
        socio_id = row[1].strip()

        catalogs["destinos"].add(destino)

        if socio_id not in catalogs["destinos_by_socio_id"]:
            catalogs["destinos_by_socio_id"][socio_id] = set()

        catalogs["destinos_by_socio_id"][socio_id].add(destino)

    # --- PAISES ---
    query_paises = """
    SELECT RTRIM(LTRIM(Pais_jot_codigo3)) AS codigo
    FROM dimensiones.tbl_Paises
    """
    for row in sql.run_query(query_paises):
        codigo = row[0]
        if codigo:
            catalogs["paises"].add(codigo.strip().upper())

    # --- DISPOSITIVOS ---
    query_dispositivos = """
    SELECT RTRIM(LTRIM(Dispositivo_codigo)) AS codigo
    FROM dimensiones.tbl_Dispositivos
    """
    for row in sql.run_query(query_dispositivos):
        codigo = row[0]
        if codigo:
            catalogs["dispositivos"].add(codigo.strip().upper())

    # --- LINEAS NEGOCIO & CONFIG. GEO ---
    query_lin_geo = """
    SELECT
        RTRIM(LTRIM(Origen_id)) AS Origen_id,
        RTRIM(LTRIM(Socio_id)) AS Socio_id,
        RTRIM(LTRIM(Canal_compra)) AS Canal_compra,
        RTRIM(LTRIM(Tipo_landing)) AS Tipo_landing,
        RTRIM(LTRIM(Gestion_departamento)) AS Gestion_departamento,
        RTRIM(LTRIM(Modelo_monetizacion)) AS Modelo_monetizacion,
        RTRIM(LTRIM(CAST(Config_geo AS VARCHAR(10)))) AS Config_geo
    FROM dimensiones.tbl_Lineas_negocio
    WHERE Origen_id = 1
        AND Socio_id = 25
    """

    for row in sql.run_query(query_lin_geo):
        origen = (row[0] or "").strip()
        socio = (row[1] or "").strip()
        canal = (row[2] or "").strip().upper()
        tipo_landing = (row[3] or "").strip().upper()
        gestion = (row[4] or "").strip().upper()
        monetizacion = (row[5] or "").strip().upper()
        config_geo = (row[6] or "").strip()

        if not (origen and socio and canal and tipo_landing and gestion and monetizacion and config_geo):
            continue

        ln_key = f"{origen}|{socio}|{canal}|{tipo_landing}|{gestion}|{monetizacion}"

        if ln_key not in catalogs["config_geo_by_ln_key"]:
            catalogs["config_geo_by_ln_key"][ln_key] = set()

        catalogs["config_geo_by_ln_key"][ln_key].add(config_geo)
    
    # --- CONTROL 9: EXCLUDED PLACEMENTS (NIVEL CUENTA) ---
    query_excluded_placements = """
    SELECT
        RTRIM(LTRIM(Dominio)) AS dominio
    FROM dimensiones.tbl_Exclusiones_dominios_automatizador
    """
    for row in sql.run_query(query_excluded_placements):
        dominio = row[0]
        if dominio:
            catalogs["excluded_placements_control_9"].add(dominio.strip().lower())

    return catalogs

# CARGA CATÁLOGO TRACKING TEMPLATES (CLAVE PLANA)
def load_tracking_templates_catalog(sql) -> dict:
    """
    Fuente: CALIDAD (Linked Server)
    Clave plana:
        SOCIO-DESTINO-TIPO_LANDING-CANAL
    Valor:
        Tracking_Template (string)
    """

    query = """
    SELECT
        Partner,
        Landings,
        Tipo_landing,
        Canal,
        Tracking_Template
    FROM OPENQUERY(
        CALIDAD,
        'SELECT
            Partner,
            Landings,
            Tipo_landing,
            Canal,
            Tracking_Template
         FROM MainBD.dimensiones.TrackingTemplates_LineaDeNegocio
         WHERE Origen = ''Google''
		   AND Partner = ''VSM''
           AND Canal <> ''TikTok'''
    )
    """

    rows = sql.run_query(query)
    catalog = {}

    for r in rows:
        if not r or len(r) < 5:
            continue

        socio = (r[0] or "").strip().upper()
        destino = (r[1] or "").strip().upper()
        tipo_landing = (r[2] or "").strip().upper()
        canal = (r[3] or "").strip().upper()
        template = (r[4] or "").strip()

        if not (socio and destino and tipo_landing and canal and template):
            continue

        clave_concat = "_".join([
            socio,
            destino,
            tipo_landing,
            canal,
        ])

        # 1 clave → 1 tracking template (como en SQL)
        catalog[clave_concat] = template

    return catalog
