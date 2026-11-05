def _extract_value(v):
    """
    Normaliza valores devueltos por GAQL.
    Puede recibir:
    - valores primitivos
    - wrappers protobuf (.value)
    - objetos con atributo .name
    """

    if v is None:
        return None

    if hasattr(v, "value"):
        return v.value

    if hasattr(v, "name"):
        return v.name

    return v


def get_assets_by_campaign(
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

    # 🔥 FILTRO CORRECTO (ENUM STRING)
    conditions.append("""
    asset_group_asset.field_type IN (
        'HEADLINE',
        'DESCRIPTION',
        'MARKETING_IMAGE',
        'LONG_HEADLINE',
        'BUSINESS_NAME',
        'SQUARE_MARKETING_IMAGE',
        'LOGO',
        'LANDSCAPE_LOGO',
        'CALL_TO_ACTION_SELECTION'
    )
    """)

    where_clause = " AND ".join(conditions)

    query = f"""
    SELECT
        asset_group.id,
        asset_group_asset.field_type,
        asset.name,
        asset.id,
        asset.text_asset.text,
        asset.image_asset.full_size.url,
        asset.call_to_action_asset.call_to_action
    FROM asset_group_asset
    WHERE {where_clause}
    """

    assets_by_group = {}

    for row in gaql.query(
        customer_id=customer_id,
        sql=query
    ):

        ag_id = _extract_value(row.get("asset_group.id"))

        if not ag_id:
            continue

        ag_id = str(ag_id)

        field_type = _extract_value(
            row.get("asset_group_asset.field_type")
        )

        asset_id = _extract_value(row.get("asset.id"))
        asset_name = _extract_value(row.get("asset.name"))

        text_asset = row.get("asset.text_asset")
        text_value = None
        if text_asset:
            text_value = _extract_value(getattr(text_asset, "text", None))

        image_asset = row.get("asset.image_asset")
        image_url = None
        if image_asset:
            image_url = _extract_value(
                getattr(image_asset.full_size, "url", None)
            )

        cta_asset = row.get("asset.call_to_action_asset")
        cta_value = None
        if cta_asset:
            raw_value = getattr(cta_asset, "call_to_action", None)
            cta_value = _extract_value(raw_value)

        value = str(text_value).strip() if text_value else None

        asset = {
            "asset_id": str(asset_id) if asset_id else None,
            "field_type": field_type,
            "name": asset_name,
            "text": value,
            "url": image_url,
            "cta": cta_value
        }

        assets_by_group.setdefault(ag_id, []).append(asset)

    return assets_by_group