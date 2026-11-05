import re

from context.data.asset_group_data import get_asset_groups_by_campaign
from context.data.asset_group_assets_data import get_assets_by_campaign
from context.data.customer_data import get_customer_data


def extract_category_id(campaign_name: str):

    if not campaign_name:
        return None

    match = re.search(r"\((\d+)\)", campaign_name)

    if match:
        return match.group(1)

    return None


def _resolve_requirements(active_controls, controls_def_map):

    requirements = {
        "needs_assets": False,
        "needs_url": False
    }

    for cid in active_controls:

        meta = controls_def_map.get(cid, {})

        if meta.get("needs_assets"):
            requirements["needs_assets"] = True

        if meta.get("needs_url"):
            requirements["needs_url"] = True

    return requirements


def build_asset_group_contexts(
    context,
    config,
    customer_id,
    campaign_id,
    active_controls,
    controls_def_map
):

    gaql = context["services"]["google_ads"]
    metrics = context["metrics"]

    # -------- QUERY 1: CUSTOMER --------

    account = get_customer_data(
        gaql,
        customer_id,
        metrics
    )

    context["account"] = account

    # -------- RESOLVER DEPENDENCIAS --------

    requirements = _resolve_requirements(
        active_controls,
        controls_def_map
    )

    needs_assets = requirements["needs_assets"]
    needs_url = requirements["needs_url"]

    # -------- QUERY 2: ASSET GROUPS --------

    asset_groups = get_asset_groups_by_campaign(
        gaql,
        customer_id,
        campaign_id,
        metrics
    )

    # -------- QUERY 3: ASSETS (SI ES NECESARIO) --------

    assets_by_group = {}

    if needs_assets:

        assets_by_group = get_assets_by_campaign(
            gaql,
            customer_id,
            campaign_id,
            metrics
        )

    contexts = []

    for ag_id, ag_data in asset_groups.items():

        campaign_id_resolved = ag_data.get("campaign_id")
        campaign_name = ag_data.get("campaign_name")

        category_id = extract_category_id(campaign_name)

        raw_assets = assets_by_group.get(ag_id, [])

        images = []
        logos = []
        text_assets = []
        asset_counts = {}

        if needs_assets:

            ASSET_FIELD_TYPE_MAP = {
                2: "HEADLINE",
                3: "DESCRIPTION",
                5: "MARKETING_IMAGE",
                17: "LONG_HEADLINE",
                18: "BUSINESS_NAME",
                19: "SQUARE_MARKETING_IMAGE",
                21: "LOGO",
                22: "LANDSCAPE_LOGO",
                25: "CALL_TO_ACTION_SELECTION"
            }

            for asset in raw_assets:

                field_type = asset.get("field_type")

                if isinstance(field_type, int):
                    field_type = ASSET_FIELD_TYPE_MAP.get(field_type, str(field_type))

                name = asset.get("name")
                text = asset.get("text")
                url = asset.get("url")
                cta = asset.get("cta")

                if field_type:
                    asset_counts[field_type] = asset_counts.get(field_type, 0) + 1

                normalized_asset = {
                    "type": field_type,
                    "name": name,
                    "text": text,
                    "url": url,
                    "cta": cta
                }

                if field_type in ("MARKETING_IMAGE", "SQUARE_MARKETING_IMAGE"):
                    images.append(normalized_asset)

                elif field_type in ("LOGO", "LANDSCAPE_LOGO"):
                    logos.append(normalized_asset)

                else:
                    text_assets.append(normalized_asset)

        ag_context = {

            "customer_id": customer_id,
            "campaign_id": campaign_id_resolved,

            "account": context.get("account", {}),

            "campaign": {
                "campaign_name": campaign_name,
                "category_id": category_id
            },

            "asset_group": ag_data
        }

        # ---- URLS ----

        if needs_url:

            ag_context["final_urls"] = ag_data.get("final_urls", [])

        # ---- ASSETS ----

        if needs_assets:

            ag_context["images"] = images
            ag_context["logos"] = logos
            ag_context["assets"] = text_assets
            ag_context["asset_counts"] = asset_counts

        # ---- REGISTRO DE CONTROLES ----

        ag_context.setdefault("controls", {})

        for cid in active_controls:
            ag_context["controls"][f"control_{cid}"] = {}

        contexts.append(ag_context)

    return contexts