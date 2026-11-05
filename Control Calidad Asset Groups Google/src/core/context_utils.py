import re
from urllib.parse import urlparse


def normalize_text(value):

    if value is None:
        return ""

    return str(value).strip()


def normalize_upper(value):

    return normalize_text(value).upper()


def equals_ignore_case(a, b):

    return normalize_upper(a) == normalize_upper(b)


def contains_ignore_case(text, expected):

    return normalize_upper(expected) in normalize_upper(text)


def extract_domain(url: str):

    url = normalize_text(url)

    if not url:
        return None

    try:
        parsed = urlparse(url)

        netloc = parsed.netloc.lower().strip()

        if netloc.startswith("www."):
            netloc = netloc[4:]

        return netloc or None

    except Exception:
        return None


def extract_first_final_url(context: dict):

    final_urls = context.get("final_urls", [])

    if not final_urls:
        asset_group = context.get("asset_group", {})
        final_urls = asset_group.get("final_urls", [])

    if not final_urls:
        return None

    return normalize_text(final_urls[0])


def extract_category_id_from_campaign_name(campaign_name: str):

    campaign_name = normalize_text(campaign_name)

    if not campaign_name:
        return None

    match = re.search(r"\((\d+)\)", campaign_name)

    if match:
        return match.group(1)

    return None


def extract_category_id_from_asset_name(asset_name: str):

    asset_name = normalize_text(asset_name)

    if not asset_name:
        return None

    match = re.search(r"\((\d+)\)", asset_name)

    if match:
        return match.group(1)

    return None


def extract_destino_from_account_name(account_name: str):

    if not account_name:
        return None

    parts = account_name.split("_")

    if len(parts) < 2:
        return None

    return parts[-2]


def build_asset_counts(assets: list):

    counts = {}

    for asset in assets or []:

        asset_type = asset.get("type") or asset.get("field_type")

        if not asset_type:
            continue

        asset_type = normalize_upper(asset_type)

        counts[asset_type] = counts.get(asset_type, 0) + 1

    return counts


def get_assets_by_type(assets: list, asset_type: str):

    asset_type = normalize_upper(asset_type)

    filtered = []

    for asset in assets or []:

        current_type = normalize_upper(
            asset.get("type") or asset.get("field_type")
        )

        if current_type == asset_type:
            filtered.append(asset)

    return filtered


def get_asset_text_values(assets: list, asset_type: str):

    filtered = get_assets_by_type(assets, asset_type)

    values = []

    for asset in filtered:

        text_value = normalize_text(asset.get("text"))

        if text_value:
            values.append(text_value)

    return values


def get_asset_name_values(assets: list, asset_type: str):

    filtered = get_assets_by_type(assets, asset_type)

    values = []

    for asset in filtered:

        name_value = normalize_text(asset.get("name"))

        if name_value:
            values.append(name_value)

    return values


def get_campaign_language(context: dict):

    campaign = context.get("campaign", {}) or {}

    return normalize_upper(
        campaign.get("language_from_name")
    )


def get_account_destino(context: dict):

    account = context.get("account", {}) or {}

    return normalize_upper(
        account.get("destino")
    )


def get_campaign_category_id(context: dict):

    campaign = context.get("campaign", {}) or {}

    category_id = campaign.get("category_id")

    if category_id:
        return normalize_text(category_id)

    campaign_name = campaign.get("campaign_name")

    return extract_category_id_from_campaign_name(campaign_name)


def safe_join_for_output(values):

    if values is None:
        return None

    if isinstance(values, (list, tuple, set)):
        clean = [normalize_text(v) for v in values if normalize_text(v)]
        return " | ".join(clean) if clean else None

    return normalize_text(values) or None