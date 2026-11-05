def aggregate_results(results):

    resumen = {}
    errores = []

    for r in results:

        customer_id = r.get("customer_id")
        campaign_id = r.get("campaign_id")
        asset_group_id = r.get("asset_group_id")

        key = f"{customer_id}_{campaign_id}_{asset_group_id}"

        row = resumen.setdefault(key, {
            "execution_user": r.get("execution_user"),
            "customer_id": customer_id,
            "customer_name": r.get("customer_name"),
            "campaign_id": campaign_id,
            "campaign_name": r.get("campaign_name"),
            "asset_group_id": asset_group_id,
            "asset_group_name": r.get("asset_group_name"),
            "status_global": "OK",
            "controles_error": [],
            "error_tecnico": None
        })

        # ---- FIX ----
        if not row.get("campaign_id") and campaign_id:
            row["campaign_id"] = campaign_id

        status = r.get("status")
        control_id = r.get("control_id")

        if status == "ERROR":

            resumen[key]["status_global"] = "ERROR"
            resumen[key]["controles_error"].append(control_id)

            errores.append(r)

        if status == "ERROR_TECNICO":

            resumen[key]["status_global"] = "ERROR_TECNICO"
            resumen[key]["error_tecnico"] = control_id

            errores.append(r)

    # convertir lista de controles a string tipo C1/C2/C3
    for row in resumen.values():

        if row["controles_error"]:
            row["controles_error"] = "/".join(row["controles_error"])
        else:
            row["controles_error"] = None

    return {
        "resumen": list(resumen.values()),
        "errores": errores
    }