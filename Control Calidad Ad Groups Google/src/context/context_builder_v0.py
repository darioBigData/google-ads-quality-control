from context.data.adgroup_data_v2 import get_adgroups_data

def build_adgroup_contexts(
    context,
    customer_id,
    campaign_id,
    ad_group_id,
    processed_ids_set=None
):

    gaql = context["services"]["google_ads"]
    metrics = context["metrics"]

    adgroups = get_adgroups_data(
        gaql,
        customer_id,
        campaign_id,
        ad_group_id,
        metrics
    )

    contexts = []

    for ag in adgroups:

        checkpoint_key = f"{customer_id}_{ag['ad_group_id']}"

        if processed_ids_set and checkpoint_key in processed_ids_set:
            continue

        ctx = {
            "customer_id": ag["customer_id"],
            "customer_name": ag["customer_name"],
            "campaign_id": ag["campaign_id"],
            "campaign_name": ag["campaign_name"],
            "ad_group": {
                "ad_group_id": ag["ad_group_id"],
                "ad_group_name": ag["ad_group_name"],
                "status": ag["status"],
                "type": ag["type"],
                "cpc_bid_micros": ag["cpc_bid_micros"],
                "bid_modifiers": ag["bid_modifiers"]
            },
            "controls": {}
        }

        contexts.append(ctx)

    return contexts


