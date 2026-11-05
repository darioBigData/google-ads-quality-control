from typing import Dict, List


def build_resumen_row(context: Dict, control_results: List[Dict], execution_user: str) -> Dict:
    technical_errors = [
        item.get("error_tecnico", "")
        for item in control_results
        if item.get("status") == "ERROR_TECNICO" and item.get("error_tecnico")
    ]

    controles_error = sum(1 for item in control_results if item.get("status") == "ERROR")
    total_controles = len(control_results)

    if technical_errors:
        status_global = "ERROR_TECNICO"
        error_tecnico = " | ".join(technical_errors)
    elif controles_error > 0:
        status_global = "ERROR"
        error_tecnico = ""
    elif total_controles > 0 and all(item.get("status") == "SKIP" for item in control_results):
        status_global = "SKIP"
        error_tecnico = ""
    else:
        status_global = "OK"
        error_tecnico = ""

    return {
        "execution_user": execution_user,
        "customer_id": context["customer_id"],
        "campaign_id": context["campaign_id"],
        "ad_group_id": context["ad_group_id"],
        "ad_id": context["ad_id"],
        "campaign_name": context["campaign"]["campaign_name"],
        "ad_group_name": context["ad_group"]["ad_group_name"],
        "ad_type": context["ad"]["type"],
        "status_global": status_global,
        "total_controles": total_controles,
        "controles_error": controles_error,
        "error_tecnico": error_tecnico
    }


def build_errores_rows(context: Dict, control_results: List[Dict], execution_user: str) -> List[Dict]:
    rows = []

    for result in control_results:
        if result.get("status") != "ERROR":
            continue

        rows.append({
            "execution_user": execution_user,
            "customer_id": context["customer_id"],
            "campaign_id": context["campaign_id"],
            "ad_group_id": context["ad_group_id"],
            "ad_id": context["ad_id"],
            "campaign_name": context["campaign"]["campaign_name"],
            "ad_group_name": context["ad_group"]["ad_group_name"],
            "control_id": result["control_id"],
            "control_name": result.get("control_name", ""),
            "valor_esperado": result.get("valor_esperado", ""),
            "valor_encontrado": result.get("valor_encontrado", ""),
            "detalle": result.get("detalle", "")
        })
    return rows