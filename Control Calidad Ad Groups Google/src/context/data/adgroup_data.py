def _normalize_status(value):
    status_map = {
        2: "ENABLED",
        3: "PAUSED",
        4: "REMOVED"
    }

    if value is None:
        return None

    if isinstance(value, str):
        return value.strip().upper()

    try:
        return status_map.get(int(value), str(value))
    except Exception:
        return str(value).strip().upper()


def _normalize_adgroup_type(value):
    type_map = {
        2: "SEARCH_STANDARD",
        3: "DISPLAY_STANDARD",
        4: "SHOPPING_PRODUCT_ADS",
        5: "HOTEL_ADS"
    }

    if value is None:
        return None

    if isinstance(value, str):
        return value.strip().upper()

    try:
        return type_map.get(int(value), str(value))
    except Exception:
        return str(value).strip().upper()


def _normalize_bid_modifier_source(value):
    source_map = {
        0: "UNSPECIFIED",
        1: "UNKNOWN",
        2: "CAMPAIGN",
        3: "AD_GROUP"
    }

    if value is None:
        return None

    if isinstance(value, str):
        return value.strip().upper()

    try:
        return source_map.get(int(value), str(value))
    except Exception:
        return str(value).strip().upper()


def get_adgroups_data(
    gaql,
    customer_id: str,
    campaign_id: str,
    metrics: dict
):

    data = {}

    # =====================================================
    # QUERY 1: AD GROUP BASE
    # =====================================================
    metrics["total_calls"] += 1

    conditions = [
        "campaign.advertising_channel_type IN ('SEARCH','DISPLAY')",
        "campaign.status IN ('ENABLED','PAUSED')"
    ]

    if campaign_id:
        conditions.append(f"campaign.id = {campaign_id}")

    where_clause = " AND ".join(conditions)

    query_ag = f"""
    SELECT
      customer.id,
      customer.descriptive_name,
      campaign.id,
      campaign.name,
      ad_group.id,
      ad_group.name,
      ad_group.status,
      ad_group.type,
      ad_group.cpc_bid_micros
    FROM ad_group
    WHERE {where_clause}
    """

    for row in gaql.query(customer_id=customer_id, sql=query_ag):

        ag_id = str(row.get("ad_group.id"))

        raw_status = row.get("ad_group.status")
        raw_type = row.get("ad_group.type")

        data[ag_id] = {
            "customer_id": customer_id,
            "customer_name": row.get("customer.descriptive_name"),
            "campaign_id": str(row.get("campaign.id")),
            "campaign_name": row.get("campaign.name"),
            "ad_group_id": ag_id,
            "ad_group_name": row.get("ad_group.name"),
            "status": _normalize_status(raw_status),
            "type": _normalize_adgroup_type(raw_type),
            "cpc_bid_micros": row.get("ad_group.cpc_bid_micros"),
            "bid_modifiers": []
        }

    # =====================================================
    # QUERY 2: BID MODIFIERS
    # =====================================================
    metrics["total_calls"] += 1

    query_bm = f"""
    SELECT
      ad_group.id,
      ad_group_bid_modifier.bid_modifier_source
    FROM ad_group_bid_modifier
    WHERE {where_clause}
    """

    for row in gaql.query(customer_id=customer_id, sql=query_bm):

        ag_id = str(row.get("ad_group.id"))

        if ag_id not in data:
            continue

        raw_bm = row.get("ad_group_bid_modifier.bid_modifier_source")
        bm = _normalize_bid_modifier_source(raw_bm)

        if bm and bm not in data[ag_id]["bid_modifiers"]:
            data[ag_id]["bid_modifiers"].append(bm)

    return list(data.values())