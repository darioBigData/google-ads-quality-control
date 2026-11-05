import os
import csv
from datetime import datetime


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def write_csv(path, rows):

    if not rows:
        return

    keys = rows[0].keys()

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def write_outputs(base_dir, resumen, errores, execution_id):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # -------- PATHS --------
    resumen_dir = os.path.join(base_dir, "output", "resumen")
    errores_dir = os.path.join(base_dir, "output", "errores")

    ensure_dir(resumen_dir)
    ensure_dir(errores_dir)

    resumen_path = os.path.join(
        resumen_dir,
        f"output_resumen_adg{execution_id}_{timestamp}.csv"
    )

    errores_path = os.path.join(
        errores_dir,
        f"output_errores_adg{execution_id}_{timestamp}.csv"
    )

    # -------- WRITE --------
    write_csv(resumen_path, resumen)
    write_csv(errores_path, errores)

    print(f"\n[OUTPUT] Resumen: {resumen_path}")
    print(f"[OUTPUT] Errores: {errores_path}")