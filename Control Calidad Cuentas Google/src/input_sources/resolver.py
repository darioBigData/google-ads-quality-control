from .csv_source import read_customer_ids_from_csv
from .sqlserver_source import read_customer_ids_from_sqlserver
from core.logger import log_line


def resolve_customer_ids(cfg: dict, services: dict, log_file) -> list[str]:
    """
    Resuelve la lista final de customer_id de forma agnóstica al origen.

    - Devuelve siempre list[str]
    - Aplica deduplicación y límites
    - Lanza error fatal si el resultado es inválido
    """

    input_cfg = cfg.get("input", {})
    mode = input_cfg.get("mode")

    if not mode:
        raise ValueError("input.mode no definido en config")

    log_line(log_file, "INFO", f"INPUT | mode={mode}")

    # RESOLUCIÓN POR ORIGEN
    if mode == "csv":
        customer_ids = read_customer_ids_from_csv(input_cfg)

    elif mode == "sqlserver":
        customer_ids = read_customer_ids_from_sqlserver(
            input_cfg=input_cfg,
            sql_service=services.get("sql_server"),
        )

    else:
        raise ValueError(f"input.mode no soportado: {mode}")

    # NORMALIZACIÓN
    customer_ids = [
        str(cid).strip()
        for cid in customer_ids
        if cid is not None and str(cid).strip()
    ]

    # DEDUPLICACIÓN (manteniendo orden)
    if input_cfg.get("deduplicate", True):
        customer_ids = list(dict.fromkeys(customer_ids))

    # LÍMITES
    max_rows = input_cfg.get("max_rows")
    if max_rows and len(customer_ids) > max_rows:
        raise ValueError(
            f"Número de cuentas ({len(customer_ids)}) supera el máximo permitido ({max_rows})"
        )

    # VALIDACIÓN FINAL
    if not customer_ids:
        raise ValueError("INPUT inválido: no se resolvieron customer_id")

    log_line(
        log_file,
        "INFO",
        f"INPUT | customer_ids_resolved={len(customer_ids)}"
    )

    return customer_ids
