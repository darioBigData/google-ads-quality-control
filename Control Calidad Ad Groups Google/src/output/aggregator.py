def aggregate_results(results: list):

    resumen_map = {}
    errores = []

    for r in results:

        key = (
            r.get("customer_id"),
            r.get("campaign_id"),
            r.get("ad_group_id")
        )

        if key not in resumen_map:

            resumen_map[key] = {
                "execution_user": r.get("execution_user"),
                "customer_id": r.get("customer_id"),
                "customer_name": r.get("customer_name"),
                "campaign_id": r.get("campaign_id"),
                "campaign_name": r.get("campaign_name"),
                "ad_group_id": r.get("ad_group_id"),
                "ad_group_name": r.get("ad_group_name"),
                "status_global": "OK",
                "controles_error": [],
                "error_tecnico": None
            }

        # -------- DETECTAR ERROR --------
        status = r.get("status")

        if status not in ("OK", "SKIP"):

            resumen_map[key]["status_global"] = "ERROR"
            resumen_map[key]["controles_error"].append(r.get("control_id"))

            errores.append(r)

        if status == "ERROR_TECNICO":
            resumen_map[key]["error_tecnico"] = "ERROR_TECNICO"

    # -------- FORMATEO FINAL --------
    resumen = []

    for v in resumen_map.values():

        v["controles_error"] = ",".join(v["controles_error"])

        resumen.append(v)

    return resumen, errores