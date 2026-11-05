# ============================================================
# CONTEXT BUILDER – QC GOOGLE ADS
# Responsabilidad:
# - Construir el contexto completo de una cuenta
# - Ejecutar GAQL
# - Normalizar datos
# - Capturar errores técnicos
# - NO ejecutar controles
# - NO decidir lógica de negocio final
# ============================================================

from core.exceptions import AccountNotProcessableError

# --- Datos base de cuenta ---
def get_account_data(gaql, customer_id: str) -> dict:
    query = """
    SELECT
      customer.descriptive_name,
      customer.currency_code,
      customer.time_zone,
      customer.auto_tagging_enabled,
      customer.tracking_url_template,
      customer.final_url_suffix,
      customer.conversion_tracking_setting.conversion_tracking_id
    FROM customer
    LIMIT 1
    """
    try: 
        rows = gaql.query(customer_id=customer_id, sql=query)


        for row in rows:
            raw_conversion_tracking_id = row.get(
                "customer.conversion_tracking_setting.conversion_tracking_id"
            )

            conversion_tracking_id = (
                int(raw_conversion_tracking_id) if raw_conversion_tracking_id else None
            )

            return {
                "customer_name": row.get("customer.descriptive_name"),
                "currency": row.get("customer.currency_code"),
                "timezone": row.get("customer.time_zone"),
                "auto_tagging_enabled": row.get("customer.auto_tagging_enabled"),
                "tracking_template": row.get("customer.tracking_url_template"),
                "final_url_suffix": row.get("customer.final_url_suffix"),
                "conversion_tracking_id": conversion_tracking_id,
            }
        
        return {}

    except Exception as e:
        error_str = str(e)

        # ERRORES DE CUENTA (NO TÉCNICOS, NO RETRY)
        if (
            "CUSTOMER_NOT_ENABLED" in error_str
            or "PERMISSION_DENIED" in error_str
            or "USER_PERMISSION_DENIED" in error_str
            or "NOT_AUTHORIZED" in error_str
            or "CUSTOMER_NOT_FOUND" in error_str
        ):
            raise AccountNotProcessableError(
                customer_id=customer_id,
                reason=error_str
            )
        
        # RESTO: ERROR TÉCNICO (RETRY / FATAL)
        raise


# --- Control 8 – Parked Domains (contexto) ---
def get_parked_domains_account_level(gaql, customer_id: str) -> dict:
    query = """
    SELECT
      customer_negative_criterion.type,
      customer_negative_criterion.content_label.type
    FROM customer_negative_criterion
    WHERE customer_negative_criterion.type = CONTENT_LABEL
      AND customer_negative_criterion.content_label.type = PARKED_DOMAIN
    """

    try:
        rows = list(gaql.query(customer_id=customer_id, sql=query))
    except Exception as e:
        return {
            "rows_returned": None,
            "error_tecnico": str(e),
        }

    return {
        "rows_returned": len(rows),
        "error_tecnico": None,
    }


# --- Control 9 – Excluded Placements (contexto) ---
def get_excluded_placements_account_level(gaql, customer_id: str, required_domains):
    import re
    from urllib.parse import urlparse

    COUNTRY_PATH_REGEX = re.compile(r"^/[a-z]{2}$")

    def normalize_domain(value: str):
        if not value:
            return None
        value = value.strip().lower()
        parsed = urlparse(value if "://" in value else f"http://{value}")
        host = parsed.netloc
        if host.startswith("www."):
            host = host[4:]
        path = parsed.path.rstrip("/")
        if path and not COUNTRY_PATH_REGEX.match(path):
            return host + path
        return host

    query = """
    SELECT
      customer_negative_criterion.placement.url
    FROM customer_negative_criterion
    WHERE customer_negative_criterion.type = 'PLACEMENT'
    """

    rows = list(gaql.query(customer_id=customer_id, sql=query))

    found = set()
    for row in rows:
        placement = row.get("customer_negative_criterion.placement")
        if placement and getattr(placement, "url", None):
            canonical = normalize_domain(placement.url)
            if canonical:
                found.add(canonical)

    required_set = set(
        normalize_domain(d) for d in required_domains if normalize_domain(d)
    )

    return {
        "required_domains": sorted(required_set),
        "found_domains": sorted(found),
        "missing_domains": sorted(required_set - found),
        "extra_domains": sorted(found - required_set),
    }


# --- Billing –> contexto base ---
def build_billing_context(gaql, customer_id: str) -> dict:
    billing_setups = []
    error_tecnico = None

    try:
        query = """
            SELECT
                billing_setup.start_date_time,
                billing_setup.end_date_time,
                billing_setup.end_time_type,
                billing_setup.id,
                billing_setup.payments_account,
                billing_setup.status
            FROM billing_setup
        """

        rows = gaql.query(customer_id=customer_id, sql=query)

        for row in rows:
            billing_setups.append({
                "billing_setup_id": row.get("billing_setup.id"),
                "start_date_time": row.get("billing_setup.start_date_time"),
                "end_date_time": row.get("billing_setup.end_date_time"),
                "end_time_type": row.get("billing_setup.end_time_type"),
                "payments_account": row.get("billing_setup.payments_account"),
                "status": row.get("billing_setup.status"),
            })

    except Exception as e:
        error_tecnico = f"{type(e).__name__}: {e}"

    return {
        "billing_setups": billing_setups,
        "error_tecnico": error_tecnico,
    }

# --- Helpers billing ---
def status_is_approved(status) -> bool:
    if status is None:
        return False
    if isinstance(status, int):
        return status == 4
    if hasattr(status, "name"):
        return status.name == "APPROVED"
    return "APPROVED" in str(status).upper()


def is_forever(end_time_type) -> bool:
    if end_time_type is None:
        return False
    if isinstance(end_time_type, int):
        return end_time_type == 3
    if hasattr(end_time_type, "name"):
        return end_time_type.name == "FOREVER"
    return "FOREVER" in str(end_time_type).upper()


def select_active_billing_setup(billing_setups: list) -> dict:
    activos = []

    for b in billing_setups:
        if (
            status_is_approved(b.get("status"))
            and is_forever(b.get("end_time_type"))
            and not b.get("end_date_time")
        ):
            activos.append(b)

    if len(activos) == 1:
        return {"active_billing_setup": activos[0], "error_tecnico": None}

    if len(activos) == 0:
        return {"active_billing_setup": None, "error_tecnico": None}

    return {
        "active_billing_setup": None,
        "error_tecnico": f"Inconsistencia billing: {len(activos)} billing_setup activos",
    }


# --- Orquestador de contexto por cuenta ---
def build_account_context(context: dict, customer_id: str):
    gaql = context["services"]["google_ads"]
    cache = context["cache"]

    context["account"] = get_account_data(gaql, customer_id)

    context["controls"]["control_8"] = get_parked_domains_account_level(
        gaql, customer_id
    )

    context["controls"]["control_9"] = get_excluded_placements_account_level(
        gaql,
        customer_id,
        cache.get("excluded_placements_control_9", []),
    )

    billing = build_billing_context(gaql, customer_id)
    selection = select_active_billing_setup(billing.get("billing_setups", []))

    context["billing"] = {
        "billing_setups": billing.get("billing_setups", []),
        "active_billing_setup": selection.get("active_billing_setup"),
        "error_tecnico": billing.get("error_tecnico") or selection.get("error_tecnico"),
    }


