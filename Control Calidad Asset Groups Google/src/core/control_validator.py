import getpass

def run_control(module, context):

    result = module.run(context)

    campaign = context.get("campaign", {})
    asset_group = context.get("asset_group", {})
    account = context.get("account", {})

    result["customer_id"] = context.get("customer_id")
    result["customer_name"] = account.get("customer_name")

    result["campaign_id"] = context.get("campaign_id")
    result["campaign_name"] = campaign.get("campaign_name")

    result["asset_group_id"] = asset_group.get("asset_group_id")
    result["asset_group_name"] = asset_group.get("asset_group_name")

    

    result["execution_user"] = getpass.getuser()

    return result