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

    rows = list(
        gaql.query(
            customer_id=customer_id,
            sql=query
        )
    )

    assets_by_group = {}

    for row in rows:

        # --- ASSET GROUP ID ---
        ag_id = _extract_value(row.get("asset_group.id"))

        if not ag_id:
            continue

        ag_id = str(ag_id)

        # --- EXTRAER CAMPOS ---

        # Tipo de campo
        field_type = _extract_value(
            row.get("asset_group_asset.field_type")
        )

        # ID del recurso
        asset_id = _extract_value(
            row.get("asset.id")
        )

        # Nombre del recurso
        asset_name = _extract_value(
            row.get("asset.name")
        )

        # Texto del recurso
        text_asset = row.get("asset.text_asset")
        
        text_value = None
        if text_asset:
            text_value = _extract_value(getattr(text_asset, "text", None))

        # Imagen del recurso
        image_asset = row.get("asset.image_asset")

        image_url = None
        if image_asset:
            image_url = _extract_value(
                getattr(image_asset.full_size, "url", None)
        )
            
        # Recurso CALL TO ACTION
        cta_asset = row.get("asset.call_to_action_asset")
        cta_value = None

        if cta_asset:
            raw_value = getattr(cta_asset, "call_to_action", None)
            cta_value = _extract_value(raw_value)
      
        # --- NORMALIZAR VALOR ---
        value = None

        if text_value:
            value = str(text_value).strip()

        
        """print("DEBUG NORMALIZED ASSET:", {
            "field_type": field_type,
            "name": asset_name,
            "text": text_value,
            "cta": cta_value
        })"""    

        # --- CONSTRUIR ASSET ---
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