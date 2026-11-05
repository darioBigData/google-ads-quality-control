"""
INPUT SQL Server

Objetivo:
- Resolver customer_id desde SQL Server vía jot_lib
- Soportar pyodbc.Row correctamente
- Mantener debugs explícitos para trazabilidad
- NO afectar al resto de la arquitectura
"""

def read_customer_ids_from_sqlserver(input_cfg: dict, sql_service, log_file=None) -> list[str]:
    print(">>> ENTRANDO EN read_customer_ids_from_sqlserver")

    if not sql_service:
        raise ValueError("SQL INPUT | Servicio SQL Server no disponible en services")

    sql_cfg = input_cfg.get("sqlserver", {})
    enabled = sql_cfg.get("enabled", False)
    query = sql_cfg.get("query")

    if not enabled:
        raise ValueError("SQL INPUT | input.sqlserver.enabled = false")

    if not query:
        raise ValueError("SQL INPUT | input.sqlserver.query no definida")

    # EJECUCIÓN QUERY
    rows = sql_service.run_query(query)

    # Intentamos materializar el iterable
    try:
        rows_list = list(rows)
    except Exception as e:
        print("SQL DEBUG | ERROR materializando rows:", e)
        rows_list = []

    customer_ids = []

    # NORMALIZACIÓN RESULTADOS (pyodbc.Row compatible)
    for idx, row in enumerate(rows_list):

        cid = None

        try:
            # pyodbc.Row es indexable (aunque no sea tuple)
            cid = row[0]
        except Exception as e:
            print(f"SQL DEBUG | ERROR extrayendo cid en fila {idx}: {e}")

        if cid is not None:
            customer_ids.append(str(cid).strip())
            
    print(f"SQL INPUT | customer_ids resueltos: {len(customer_ids)}")

    if not customer_ids:
        raise ValueError(
            "SQL INPUT | No se resolvió ningún customer_id. "
            "Revisar entorno SQL, query y formato devuelto por run_query."
        )

    return customer_ids
