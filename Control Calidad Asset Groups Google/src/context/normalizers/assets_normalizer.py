def normalize_assets(assets):

    assets_by_type = {}

    for asset in assets:

        field_type = asset.get("field_type")
        value = asset.get("text")

        if not field_type or not value:
            continue

        field_type = str(field_type).strip().upper()

        assets_by_type.setdefault(field_type, []).append(value)

    asset_counts = {
        k: len(v)
        for k, v in assets_by_type.items()
    }

    return assets_by_type, asset_counts