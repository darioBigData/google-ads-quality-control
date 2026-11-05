def run(context: dict) -> dict:
    control_id = "1"

    # Traemos el nombre de cuenta y la cache desde el context
    account_name = context.get("account", {}).get("customer_name")
    cache = context.get("cache", {})

    # Constantes de mapeos del control
    SOCIO_SQL_TO_ID = {
        "IAC": "3",
        "VSM": "25"
    }
    
    LINEA_NEGOCIO_TO_CANAL = {
    "SC": "Search",
    "DS": "GDN",
    "PM": "Performance MAX",
    "UP": "Search",
    "DG": "DemGen"
    }

    if not account_name:
        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": "Nombre de cuenta disponible en contexto",
            "valor_encontrado": None,
            "detalle": "Nombre de cuenta no disponible",
            "error_tecnico": "No se pudo obtener customer.descriptive_name"
        }

    bloques = account_name.split("_")

    if len(bloques) != 9:
        return {
            "control_id": control_id,
            "status": "ERROR",
            "valor_esperado": "Nombre con 9 bloques separados por '_'",
            "valor_encontrado": account_name,
            "detalle": "Estructura incorrecta del nombre de la cuenta",
            "error_tecnico": f"Numero de bloques incorrecto: {len(bloques)}"
        }
    
    
    # -------- BLOQUE 1 — PAÍS --------
    pais = bloques[0].strip().upper()
    if pais not in cache.get("paises", set()):
        return {
            "control_id": control_id,
            "status": "ERROR",
            "valor_esperado": "Codigo de pais valido",
            "valor_encontrado": pais,
            "detalle": "Nombre de cuenta invalido",
            "error_tecnico": "Bloque 1 – Pais no encontrado en catalogo JOT"
        }

    # -------- BLOQUE 2 — DIVISA --------
    divisa = bloques[1].strip().upper()
    if divisa != "HKD":
        return {
            "control_id": control_id,
            "status": "ERROR",
            "valor_esperado": "HKD",
            "valor_encontrado": divisa,
            "detalle": "Nombre de cuenta invalido",
            "error_tecnico": "Bloque 2 – Divisa incorrecta"
        }

    # -------- BLOQUE 3 — ORDINAL --------
    ordinal = bloques[2].strip()
    if not (ordinal.isdigit() and 1 <= int(ordinal) <= 999):
        return {
            "control_id": control_id,
            "status": "ERROR",
            "valor_esperado": "Ordinal entre 001 y 999",
            "valor_encontrado": ordinal,
            "detalle": "Nombre de cuenta invalido",
            "error_tecnico": "Bloque 3 – Ordinal inválido"
        }

    # -------- BLOQUE 4 — DISPOSITIVO --------
    dispositivo = bloques[3].strip().upper()
    if dispositivo not in cache.get("dispositivos", set()):
        return {
            "control_id": control_id,
            "status": "ERROR",
            "valor_esperado": "Codigo de dispositivo valido",
            "valor_encontrado": dispositivo,
            "detalle": "Nombre de cuenta invalido",
            "error_tecnico": "Bloque 4 – Dispositivo no encontrado en catalogo JOT"
        }

    # -------- BLOQUE 5 — CONCORDANCIA --------
    concordancia = bloques[4].strip().upper()
    if concordancia not in {"A", "F", "E", "X"}:
        return {
            "control_id": control_id,
            "status": "ERROR",
            "valor_esperado": "A / F / E / X",
            "valor_encontrado": concordancia,
            "detalle": "Nombre de cuenta invalido",
            "error_tecnico": "Bloque 5 – Concordancia invalida"
        }

    # -------- BLOQUE 6 — LÍNEA DE NEGOCIO --------
    linea_negocio = bloques[5].strip().upper()
    if linea_negocio not in {"SC", "DS", "PM", "UP", "DG"}:
        return {
            "control_id": control_id,
            "status": "ERROR",
            "valor_esperado": "SC / DS / PM / UP / DG",
            "valor_encontrado": linea_negocio,
            "detalle": "Nombre de cuenta invalido",
            "error_tecnico": "Bloque 6 – Linea de negocio invalida"
        }

    # -------- BLOQUE 7 — SOCIO --------
    SOCIO_NOMENCLATURA_TO_SQL = {
        "ACD": "IAC",
        "JOT": "VSM"
    }

    socio_raw = bloques[6].strip().upper()
    socio_sql = SOCIO_NOMENCLATURA_TO_SQL.get(socio_raw)

    if not socio_sql or socio_sql not in cache.get("socios", set()):
        return {
            "control_id": control_id,
            "status": "ERROR",
            "valor_esperado": "Socio valido",
            "valor_encontrado": socio_raw,
            "detalle": "Nombre de cuenta invalido",
            "error_tecnico": "Bloque 7 – Socio no valido"
        }

    # -------- BLOQUE 8 — DESTINO --------
    # 1️. Validación de existencia del catálogo
    destino = bloques[7].strip().upper()
    destinos_catalogo = cache.get("destinos")
    destinos_por_socio = cache.get("destinos_by_socio_id")

    if not destinos_catalogo or not destinos_por_socio:
        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": "Catalogo de destinos cargado",
            "valor_encontrado": destino,
            "detalle": "No existe catalogo de destinos en cache",
            "error_tecnico": "destinos o destinos_by_socio_id no disponibles"
        }

    # 2️. Validación de existencia del destino
    if destino not in destinos_catalogo:
        return {
            "control_id": control_id,
            "status": "ERROR",
            "valor_esperado": "Destino valido",
            "valor_encontrado": destino,
            "detalle": "Destino no reconocido",
            "error_tecnico": None
        }

    socio_id = SOCIO_SQL_TO_ID.get(socio_sql)

    if not socio_id:
        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": "Socio con ID valido",
            "valor_encontrado": socio_sql,
            "detalle": "No existe mapping de socio a Socio_id",
            "error_tecnico": f"Mapping no definido para socio_sql={socio_sql}"
        }

    if socio_id not in destinos_por_socio:
        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": "Socio con destinos definidos",
            "valor_encontrado": socio_sql,
            "detalle": "No existe definición de destinos para el socio",
            "error_tecnico": f"destinos_by_socio_id no definido para socio_id={socio_id}"
        }

    # 3. Validación de coherencia destino ↔ socio
    if destino not in destinos_por_socio[socio_id]:
        return {
            "control_id": control_id,
            "status": "ERROR",
            "valor_esperado": f"Destino válido para socio {socio_sql}",
            "valor_encontrado": destino,
            "detalle": "Destino no coherente con el socio de la cuenta",
            "error_tecnico": None
        }

    # -------- BLOQUE 9 — CONFIG GEO --------
    config_geo = bloques[8].strip()
    if not (config_geo.isdigit() and len(config_geo) == 3):
        return {
            "control_id": control_id,
            "status": "ERROR",
            "valor_esperado": "Config geo de 3 digitos",
            "valor_encontrado": config_geo,
            "detalle": "Bloque 9 – Config geo invalida",
            "error_tecnico": None
        }

    """ --- Validación contra catálogo SQL de líneas de negocio ---
    NOTA:
        - El control NO construye tipo_landing, gestión ni monetización
        - Se valida contra cualquier combinación compatible definida en SQL
    """
    origen_id = "1"  # Google (fijo)

    canal_compra = LINEA_NEGOCIO_TO_CANAL.get(linea_negocio)
    if not canal_compra:
        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": "Canal de compra valido para línea de negocio",
            "valor_encontrado": linea_negocio,
            "detalle": "No existe mapeo de linea de negocio a Canal_compra",
            "error_tecnico": f"Mapeo no definido para linea_negocio={linea_negocio}"
        }

    catalogo_geo = cache.get("config_geo_by_ln_key")
    if not catalogo_geo:
        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": "Catalogo de lineas de negocio cargado",
            "valor_encontrado": None,
            "detalle": "No existe catalogo config_geo_by_ln_key en cache",
            "error_tecnico": "config_geo_by_ln_key no disponible"
        }

    # En SQL_catalogs.py la ln_key se normaliza a UPPER:
    prefix = (
        f"{str(origen_id).strip().upper()}|"
        f"{str(socio_id).strip().upper()}|"
        f"{str(canal_compra).strip().upper()}|"
    )

    # Buscamos cualquier línea de negocio compatible (independiente de tipo_landing / gestión / monetización)
    matched_keys = [
        k for k in catalogo_geo.keys()
        if isinstance(k, str) and k.startswith(prefix)
    ]

    if not matched_keys:
        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": "Definicion de linea de negocio existente en catalogo SQL",
            "valor_encontrado": config_geo,
            "detalle": "No existe ninguna linea de negocio compatible en catalogo",
            "error_tecnico": f"No se encontraron claves con prefijo {prefix}"
        }

    # Si cualquier combinación compatible permite el config_geo → OK
    permitido = any(
        config_geo in catalogo_geo.get(k, set())
        for k in matched_keys
    )

    if not permitido:
        return {
            "control_id": control_id,
            "status": "ERROR",
            "valor_esperado": "Config geo permitido para la linea de negocio",
            "valor_encontrado": config_geo,
            "detalle": "Config geo no permitido segun catálogo de lineas de negocio",
            "error_tecnico": None
        }

    # Incluimos en el contexto de la cuenta los siguientes valores
    context.setdefault("account", {})
    context["account"]["socio"] = socio_sql
    context["account"]["destino"] = destino
    context["account"]["linea_negocio"] = linea_negocio
    context["account"]["config_geo"] = int(config_geo)
    context["account"]["canal_compra"] = canal_compra


    return {
        "control_id": control_id,
        "status": "OK",
        "valor_esperado": "Nombre de cuenta valido y coherente con linea_negocio & config_geo",
        "valor_encontrado": account_name,
        "detalle": "Nombre de cuenta valido",
        "error_tecnico": None
    }
