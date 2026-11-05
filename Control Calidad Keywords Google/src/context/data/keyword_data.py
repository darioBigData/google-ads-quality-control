def parse_enum(value):
    if value is None:
        return None

    # Caso enum con .name (protobuf)
    name = getattr(value, "name", None)
    if isinstance(name, str) and name:
        return name.strip().upper()

    # Caso string
    if isinstance(value, str):
        return value.strip().upper()

    # Caso numérico
    try:
        return str(int(value))
    except Exception:
        return str(value).strip().upper()


def get_keywords(gaql, customer_id, campaign_id=None, ad_group_id=None):

    query = """
    SELECT
        ad_group_criterion.resource_name,
        ad_group_criterion.criterion_id,
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type,
        ad_group_criterion.approval_status,
        ad_group_criterion.negative,
        campaign.id,
        campaign.name,
        customer.descriptive_name,
        ad_group.id
    FROM ad_group_criterion
    WHERE ad_group_criterion.type = KEYWORD
    AND ad_group_criterion.keyword.text IS NOT NULL
    """

    if campaign_id:
        query += f" AND campaign.id = {campaign_id}"

    if ad_group_id:
        query += f" AND ad_group.id = {ad_group_id}"

    print(f"\n[DEBUG][KEYWORDS] Query lanzada | customer_id={customer_id}")

    rows = list(gaql.query(customer_id=customer_id, sql=query))

    entities = []

    # =========================
    # MAPPINGS NEGOCIO
    # =========================
    MATCH_TYPE_MAP = {
        "2": "EXACT", 
        "3": "PHRASE", 
        "4": "BROAD"
    }

    APPROVAL_STATUS_MAP = {
        "2": "APPROVED",
        "3": "DISAPPROVED",
        "4": "PENDING"
    }

    for i, row in enumerate(rows):

        resource_name = row.get("ad_group_criterion.resource_name")
        customer_name = row.get("customer.descriptive_name")
        campaign_name = row.get("campaign.name")        
        campaign_id_str = str(row.get("campaign.id"))
        ad_group_id_str = str(row.get("ad_group.id"))


        # =========================
        # 🔥 ACCESO CORRECTO AL OBJETO KEYWORD
        # =========================
        keyword_obj = row.get("ad_group_criterion.keyword")

        raw_match_type = None
        keyword_text = None

        if keyword_obj:
            raw_match_type = getattr(keyword_obj, "match_type", None)
            keyword_text = getattr(keyword_obj, "text", None)

        raw_approval_status = row.get("ad_group_criterion.approval_status")
        is_negative = row.get("ad_group_criterion.negative")

        # =========================
        # NORMALIZACIÓN
        # =========================
        match_type_enum = parse_enum(raw_match_type)
        approval_status_enum = parse_enum(raw_approval_status)

        # =========================
        # MAPPING NEGOCIO
        # =========================
        match_type = MATCH_TYPE_MAP.get(match_type_enum)
        approval_status = APPROVAL_STATUS_MAP.get(approval_status_enum)

        # =========================
        # ENTITY
        # =========================
        entities.append({
            "customer_id": customer_id,
            "customer_name": customer_name,
            "campaign_id": campaign_id_str,
            "campaign_name": campaign_name,
            "ad_group_id": ad_group_id_str,
            "entity_type": "keyword",
            "entity_id": resource_name,
            "entity": {
                "type": "keyword",
                "id": resource_name,
                "raw": {
                    "match_type": match_type,
                    "match_type_raw": match_type_enum,
                    "approval_status": approval_status,
                    "approval_status_raw": approval_status_enum,
                    "is_negative": is_negative,
                    "criterion_id": row.get("ad_group_criterion.criterion_id"),
                    "resource_name": resource_name
                }
            }
        })

    print(f"\n[DEBUG][KEYWORDS] TOTAL: {len(entities)}")

    return entities