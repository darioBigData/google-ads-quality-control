import csv
import os
from datetime import datetime


def write_outputs(root_path, aggregated, execution_id=None, suffix=""):

    if execution_id:
        timestamp = execution_id
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    resumen_path = os.path.join(
        root_path,
        "output",
        "resumen",
        f"output_resumen_ag{suffix}_{timestamp}.csv"
    )

    errores_path = os.path.join(
        root_path,
        "output",
        "errores",
        f"output_errores_ag{suffix}_{timestamp}.csv"
    )

    os.makedirs(os.path.dirname(resumen_path), exist_ok=True)
    os.makedirs(os.path.dirname(errores_path), exist_ok=True)

    # --------------------------------------------------
    # ORDEN DE COLUMNAS
    # --------------------------------------------------

    resumen_fields = [
        "execution_user",
        "customer_id",
        "customer_name",
        "campaign_id",
        "campaign_name",
        "asset_group_id",
        "asset_group_name",
        "status_global",
        "controles_error",
        "error_tecnico"
    ]

    errores_fields = [
        "execution_user",
        "customer_id",
        "customer_name",
        "campaign_id",
        "campaign_name",
        "asset_group_id",
        "asset_group_name",
        "control_id",
        "status",
        "valor_esperado",
        "valor_encontrado",
        "detalle",
        "error_tecnico"
    ]

    resumen = aggregated["resumen"]
    errores = aggregated["errores"]

    # -------- RESUMEN --------

    if resumen:

        with open(resumen_path, "w", newline="", encoding="utf-8-sig") as f:

            writer = csv.DictWriter(
                f,
                fieldnames=resumen_fields,
                delimiter=";",
                extrasaction="ignore"
            )

            writer.writeheader()

            for r in resumen:
                writer.writerow(r)

        print(f"Output resumen generado: {resumen_path}")

    # -------- ERRORES --------

    if errores:

        with open(errores_path, "w", newline="", encoding="utf-8-sig") as f:

            writer = csv.DictWriter(
                f,
                fieldnames=errores_fields,
                delimiter=";",
                extrasaction="ignore"
            )

            writer.writeheader()

            for r in errores:
                writer.writerow(r)

        print(f"Output errores generado: {errores_path}")