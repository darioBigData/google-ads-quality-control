import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.input_validator import validate_input_file
from context.data.keyword_data import get_keywords
from context.data.asset_data import get_assets


def build_contexts(config):

    jotlib_path = config["paths"]["jotlib_path"]

    if jotlib_path not in sys.path:
        sys.path.insert(0, jotlib_path)

    from jot.jot_googleads.auth import GoogleAdsAuth  # type: ignore
    from jot.jot_googleads.services.gaql import GAQLService  # type: ignore

    auth = GoogleAdsAuth(
        module_path=os.path.join(jotlib_path, "jot", "jot_googleads")
    )
    client = auth.get_client()
    gaql = GAQLService(client)

    input_path = config["paths"]["input_csv_path"]

    # =========================
    # VALIDACIÓN INPUT
    # =========================
    rows = validate_input_file(input_path)

    all_entities = []

    for row in rows:

        customer_id = row["customer_id"]
        campaign_id = row.get("campaign_id")
        ad_group_id = row.get("ad_group_id")

        # =========================
        # KEYWORDS
        # =========================
        keyword_entities = get_keywords(
            gaql,
            customer_id,
            campaign_id,
            ad_group_id
        )

        # =========================
        # ASSETS + COUNTS
        # =========================
        asset_entities, campaign_assets_count = get_assets(
            gaql,
            customer_id,
            campaign_id
        )

        # =========================
        # UNIFICAR ENTIDADES
        # =========================
        entities = keyword_entities + asset_entities

        # =========================
        # ENRIQUECER CONTEXT
        # =========================
        for entity in entities:

            campaign_id_entity = entity.get("campaign_id")

            entity["campaign_assets_count"] = campaign_assets_count.get(
                campaign_id_entity,
                {
                    "sitelink": 0,
                    "callout": 0,
                    "snippet": 0
                }
            )

            all_entities.append(entity)

    # =========================
    # DEDUPLICACIÓN GLOBAL
    # =========================
    seen = set()
    unique_entities = []

    for e in all_entities:
        key = f"{e['customer_id']}|{e['entity_type']}|{e['entity_id']}"
        if key not in seen:
            seen.add(key)
            unique_entities.append(e)

    return unique_entities