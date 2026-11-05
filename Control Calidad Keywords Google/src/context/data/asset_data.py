def parse_enum(value):
    if value is None:
        return None

    name = getattr(value, "name", None)
    if isinstance(name, str) and name:
        return name.strip().upper()

    if isinstance(value, str):
        return value.strip().upper()

    try:
        return str(int(value))
    except Exception:
        return str(value).strip().upper()


def get_assets(gaql, customer_id, campaign_id=None):

    query = """
    SELECT
        customer.descriptive_name,
        campaign.id,
        campaign.name,
        campaign_asset.field_type
    FROM campaign_asset
    """

    if campaign_id:
        query += f" WHERE campaign.id = {campaign_id}"

    print(f"\n[DEBUG][ASSETS] Query lanzada | customer_id={customer_id}")

    rows = list(gaql.query(customer_id=customer_id, sql=query))

    entities = []

    campaign_assets_count = {}

    mapping = {
        13: "sitelink",
        11: "callout",
        12: "snippet"
    }

    for i, row in enumerate(rows):

        customer_name = row.get("customer.descriptive_name")
        raw_field_type = row.get("campaign_asset.field_type")
        entity_type = mapping.get(raw_field_type)
        campaign_id_str = str(row.get("campaign.id"))
        campaign_name = row.get("campaign.name")
        resource_name = row.get("campaign_asset.resource_name")
        
        # =========================
        # DEBUG CLAVE
        # =========================

        if not entity_type:
            continue

        if campaign_id_str not in campaign_assets_count:
            campaign_assets_count[campaign_id_str] = {
                "sitelink": 0,
                "callout": 0,
                "snippet": 0
            }

        campaign_assets_count[campaign_id_str][entity_type] += 1


        entities.append({
            "customer_id": customer_id,
            "customer_name": customer_name,
            "campaign_id": campaign_id_str,
            "campaign_name": campaign_name,
            "ad_group_id": None,
            "entity_type": entity_type,
            "entity_id": resource_name,
            "entity": {
                "type": entity_type,
                "id": resource_name,
                "raw": {
                    "field_type": raw_field_type,
                    "resource_name": resource_name
                }
            }
        })

    # =========================
    # RESUMEN FINAL
    # =========================
    print(f"\n[DEBUG][ASSETS] TOTAL ENTIDADES: {len(entities)}")
    print(f"[DEBUG][ASSETS] CONTEO FINAL:")
    for camp_id, counts in campaign_assets_count.items():
        print(f"  Campaign {camp_id}: {counts}")

    return entities, campaign_assets_count