def get_asset_groups_by_campaign(
    gaql,
    customer_id: str,
    campaign_id: str,
    metrics: dict
):

    metrics["total_calls"] += 1

    campaign_id = str(campaign_id).strip() if campaign_id else None

    conditions = []

    if campaign_id:
        conditions.append(f"campaign.id = {campaign_id}")

    conditions.append("campaign.advertising_channel_type = 'PERFORMANCE_MAX'")

    where_clause = " AND ".join(conditions)

    query = f"""
    SELECT
        campaign.id,
        campaign.name,
        asset_group.id,
        asset_group.name,
        asset_group.status,
        asset_group.final_urls
    FROM asset_group
    WHERE {where_clause}
    """

    rows = list(gaql.query(customer_id=customer_id, sql=query))

    asset_groups = {}

    for row in rows:

        ag_id = row.get("asset_group.id")

        if not ag_id:
            continue

        asset_groups[str(ag_id)] = {
            "asset_group_id": str(ag_id),
            "asset_group_name": row.get("asset_group.name"),
            "status": row.get("asset_group.status"),
            "final_urls": list(row.get("asset_group.final_urls") or []),
            "campaign_id": row.get("campaign.id"),
            "campaign_name": row.get("campaign.name")
        }

    return asset_groups