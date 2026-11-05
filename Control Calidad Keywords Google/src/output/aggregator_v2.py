def build_output_rows(results, execution_user=None):

    campaign_map = {}
    error_map = {}  # NUEVO: agrupación errores

    for item in results:

        context = item["entity"]
        control_results = item.get("results", [])
        entity_tech_error = item.get("entity_tech_error")

        customer_id = context.get("customer_id")
        customer_name = context.get("customer_name")

        campaign_id = context.get("campaign_id")
        campaign_name = context.get("campaign_name")

        key = f"{customer_id}|{campaign_id}"

        if key not in campaign_map:
            campaign_map[key] = {
                "execution_user": execution_user,
                "customer_id": customer_id,
                "customer_name": customer_name,
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "status_list": [],
                "control_ids_error": set(),
                "control_ids_executed": set(),
                "error_tecnico": False
            }

        campaign_data = campaign_map[key]

        # =========================
        # ERROR TÉCNICO
        # =========================
        if entity_tech_error:
            campaign_data["error_tecnico"] = True

        # =========================
        # CONTROLES
        # =========================
        for r in control_results:

            status = r.get("status")
            control_id = r.get("control_id")

            if status != "SKIP":
                campaign_data["control_ids_executed"].add(control_id)

            campaign_data["status_list"].append(status)

            if status == "ERROR":
                campaign_data["control_ids_error"].add(control_id)

                # =========================
                # ERROR AGRUPADO (CAMPAÑA + CONTROL)
                # =========================
                error_key = f"{customer_id}|{campaign_id}|{control_id}"

                if error_key not in error_map:
                    error_map[error_key] = {
                        "execution_user": execution_user,
                        "customer_id": customer_id,
                        "campaign_id": campaign_id,
                        "campaign_name": campaign_name,
                        "ad_group_id": None,
                        "entity_id": None,
                        "entity_type": "campaign",
                        "control_id": control_id,
                        "control_name": r.get("control_name"),
                        "valor_esperado": r.get("valor_esperado"),
                        "valor_encontrado": r.get("valor_encontrado"),
                        "detalle": r.get("detalle")
                    }

    # =========================
    # BUILD SUMMARY
    # =========================
    summary_rows = []

    for _, data in campaign_map.items():

        if data["error_tecnico"]:
            status_global = "ERROR_TECNICO"
        elif any(s == "ERROR" for s in data["status_list"]):
            status_global = "ERROR"
        else:
            status_global = "OK"

        controles_error = (
            "0"
            if not data["control_ids_error"]
            else ",".join(sorted(data["control_ids_error"]))
        )

        summary_rows.append({
            "execution_user": data["execution_user"],
            "customer_id": data["customer_id"],
            "customer_name": data["customer_name"],
            "campaign_id": data["campaign_id"],
            "campaign_name": data["campaign_name"],
            "status_global": status_global,
            "total_controles": len(data["control_ids_executed"]),
            "controles_error": controles_error,
            "error_tecnico": data["error_tecnico"]
        })

    # =========================
    # CONVERT ERROR MAP → LIST
    # =========================
    error_rows = list(error_map.values())

    return summary_rows, error_rows