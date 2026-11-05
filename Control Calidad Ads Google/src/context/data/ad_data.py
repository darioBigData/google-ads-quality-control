# AD DATA ACCESS

def get_ads_by_scope(gaql, input_row: dict, metrics: dict) -> list:

    metrics["total_calls"] += 1

    # --------------------------------------------------
    # NORMALIZACIÓN DE INPUT
    # --------------------------------------------------
    customer_id = str(input_row.get("customer_id", "")).strip()
    campaign_id = str(input_row.get("campaign_id", "")).strip()
    ad_group_id = str(input_row.get("ad_group_id", "")).strip()

    # --------------------------------------------------
    # WHERE DINÁMICO
    # --------------------------------------------------
    where_clauses = [
        f"customer.id = {customer_id}"
    ]

    if campaign_id:
        where_clauses.append(f"campaign.id = {campaign_id}")

    if ad_group_id:
        where_clauses.append(f"ad_group.id = {ad_group_id}")

    print("--------------------------------------------------")
    print("[DATA] customer_id:", customer_id)
    print("[DATA] campaign_id:", campaign_id)
    print("[DATA] ad_group_id:", ad_group_id)
    print("[DATA] WHERE:", " AND ".join(where_clauses))

    # --------------------------------------------------
    # QUERY GAQL (CORRECTA)
    # --------------------------------------------------
    query = f"""
    SELECT
        customer.id,
        customer.descriptive_name,
        campaign.id,
        campaign.name,
        campaign.advertising_channel_type,
        ad_group.id,
        ad_group.name,
        ad_group_ad.status,
        ad_group_ad.ad.id,
        ad_group_ad.ad.type,
        ad_group_ad.ad.final_urls
    FROM ad_group_ad
    WHERE {' AND '.join(where_clauses)}
    """

    rows = list(gaql.query(customer_id=customer_id, sql=query))

    ads = []

    for row in rows:
        ads.append(_normalize_ad_row(row))

    return ads


# NORMALIZACIÓN

def _normalize_ad_row(row: dict) -> dict:

    # --------------------------------------------------
    # STATUS
    # --------------------------------------------------
    STATUS_MAP = {
        2: "ENABLED",
        3: "PAUSED",
        4: "REMOVED"
    }

    raw_status = row.get("ad_group_ad.status")

    try:
        raw_status_int = int(raw_status)
    except (TypeError, ValueError):
        raw_status_int = raw_status

    status_norm = STATUS_MAP.get(raw_status_int, raw_status)

    # --------------------------------------------------
    # 🔥 AD OBJECT (CLAVE)
    # --------------------------------------------------
    ad_obj = row.get("ad_group_ad.ad")

    ad_id = None
    ad_type = None
    final_urls = []

    # 🔥 Mapping mínimo basado en TU realidad
    AD_TYPE_MAP = {
        15: "RESPONSIVE_SEARCH_AD"
    }

    if ad_obj:
        try:
            ad_id = str(ad_obj.id)
        except Exception:
            ad_id = None

        # 🔥 NORMALIZACIÓN CONTROLADA
        try:
            raw_type = ad_obj.type_

            try:
                raw_type_int = int(raw_type)
            except (TypeError, ValueError):
                raw_type_int = None

            ad_type = AD_TYPE_MAP.get(
                raw_type_int,
                str(raw_type_int) if raw_type_int is not None else None
            )

        except Exception:
            ad_type = None

        try:
            final_urls = [str(u).strip() for u in ad_obj.final_urls]
        except Exception:
            final_urls = []

    print("[DATA] ad_id:", ad_id)
    print("[DATA] ad_type:", ad_type)
    print("[DATA] final_urls:", final_urls)

    # --------------------------------------------------
    # CAMPAIGN TYPE
    # --------------------------------------------------
    CAMPAIGN_TYPE_MAP = {
        2: "SEARCH",
        3: "DISPLAY",
        6: "VIDEO",
        10: "PERFORMANCE_MAX"
    }

    raw_campaign_type = row.get("campaign.advertising_channel_type")

    try:
        raw_campaign_type_int = int(raw_campaign_type)
    except (TypeError, ValueError):
        raw_campaign_type_int = raw_campaign_type

    campaign_type_norm = CAMPAIGN_TYPE_MAP.get(
        raw_campaign_type_int,
        str(raw_campaign_type).strip()
    )

    return {
        "customer_id": str(row.get("customer.id", "")).strip(),
        "account_name": str(row.get("customer.descriptive_name", "")).strip(),

        "campaign_id": str(row.get("campaign.id", "")).strip(),
        "campaign_name": str(row.get("campaign.name", "")).strip(),
        "campaign_type": campaign_type_norm,

        "ad_group_id": str(row.get("ad_group.id", "")).strip(),
        "ad_group_name": str(row.get("ad_group.name", "")).strip(),

        "ad_id": ad_id,
        "ad_status": status_norm,
        "ad_type": ad_type,
        "final_urls": final_urls
    }