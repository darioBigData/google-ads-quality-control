def run(context: dict) -> dict:
    """
    Control 2 - Línea de negocio

    Valida que la línea de negocio indicada en el nombre de la cuenta
    sea coherente con los tipos de campañas ACTIVAS o PAUSADAS existentes en la cuenta.

    Reglas:
    - Solo se tienen en cuenta campañas ACTIVAS
    - Si no hay campañas activas -> SKIP
    - Si hay campañas activas incompatibles -> ERROR
    """

    control_id = "2"

    try:
        # 1. Obtener línea de negocio desde el nombre cuenta
        account = context.get("account", {})
        linea_negocio = account.get("linea_negocio")

        if not linea_negocio:
            return {
                "control_id": control_id,
                "status": "ERROR",
                "valor_esperado": "Nombre de cuenta con linea de negocio",
                "valor_encontrado": None,
                "detalle": "La linea de negocio no se pudo obtener del nombre de la cuenta", 
                "error_tecnico": "Contexto incompleto: linea_negocio"
            }

        # 2. Obtener campañas activas
        gaql = context.get("services", {}).get("google_ads")
        customer_id = context.get("input", {}).get("customer_id")

        if not gaql or not customer_id:
            return {
                "control_id": control_id,
                "status": "ERROR_TECNICO",
                "valor_esperado": "Acceso a Google Ads API",
                "valor_encontrado": None,
                "detalle": "Servicio Google Ads no disponible",
                "error_tecnico": "GAQL no inicializado"
            }

        query = """
        SELECT
          campaign.advertising_channel_type,
          campaign.status
        FROM campaign
        WHERE campaign.status != 'REMOVED'
        """

        rows = gaql.query(
            customer_id=customer_id.replace("-", ""),
            sql=query
        )

        tipos_campaña_activos = set()

        CHANNEL_TYPE_MAP = {
                2: "SEARCH",
                3: "DISPLAY",
                10: "PERFORMANCE_MAX",
                14: "DEMGEN"
            }

        for row in rows:
            raw_type = row.get("campaign.advertising_channel_type")
            channel_type = CHANNEL_TYPE_MAP.get(raw_type)       
            if channel_type:
                tipos_campaña_activos.add(channel_type)
                
        # 3. Caso sin campañas activas -> SKIP
        if not tipos_campaña_activos:
            return {
                "control_id": control_id,
                "status": "SKIP",
                "valor_esperado": "Campañas activas coherentes con la linea de negocio",
                "valor_encontrado": [],
                "detalle": "No existen campañas activas",
                "error_tecnico": None
            }

        # 4. Mapa línea de negocio -> tipos permitidos
        expected_map = {
            "SC": {"SEARCH"},
            "PM": {"PERFORMANCE_MAX"},
            "DS": {"DISPLAY"},
            "DG": {"DEMGEN"},
            "UP": {"SEARCH"}
        }

        expected_types = expected_map.get(linea_negocio)

        if not expected_types:
            return {
                "control_id": control_id,
                "status": "ERROR",
                "valor_esperado": "Linea de negocio valida (SC, PM, DS, DG, UP)",
                "valor_encontrado": linea_negocio,
                "detalle": "Linea de negocio no reconocida",
                "error_tecnico": None
            }

        # 5. Validación coherencia
        if tipos_campaña_activos.issubset(expected_types):
            status = "OK"
            detalle = "Tipos de campaña coherentes con la linea de negocio"
            
        else:
            status = "ERROR"
            detalle = "Existen campañas incompatibles con la linea de negocio"

        return {
            "control_id": control_id,
            "status": status,
            "valor_esperado": f"Tipos permitidos: {sorted(expected_types)}",
            "valor_encontrado": sorted(tipos_campaña_activos),
            "detalle": detalle,
            "error_tecnico": None
        }

    except Exception as e:
        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": "Validacion linea de negocio",
            "valor_encontrado": None,
            "detalle": "Excepcion no controlada",
            "error_tecnico": str(e)
        }
