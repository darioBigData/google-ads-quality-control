import os
import csv


def write_outputs(summary_rows, error_rows, config, run_id):

    output_dir = config["paths"]["output_dir"]

    resumen_dir = os.path.join(output_dir, "resumen")
    errores_dir = os.path.join(output_dir, "errores")

    os.makedirs(resumen_dir, exist_ok=True)
    os.makedirs(errores_dir, exist_ok=True)

    resumen_path = os.path.join(
        resumen_dir,
        f"{config['output']['filenames']['summary_prefix']}_{run_id}.csv"
    )

    errores_path = os.path.join(
        errores_dir,
        f"{config['output']['filenames']['detail_prefix']}_{run_id}.csv"
    )

    if summary_rows:
        with open(resumen_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=summary_rows[0].keys(),
                delimiter=";"
            )
            writer.writeheader()
            writer.writerows(summary_rows)

    if error_rows:
        with open(errores_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=error_rows[0].keys(),
                delimiter=";"
            )
            writer.writeheader()
            writer.writerows(error_rows)