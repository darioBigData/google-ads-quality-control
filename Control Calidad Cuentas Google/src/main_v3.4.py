import os
import sys
import json
import csv
import datetime
import getpass
import socket
import importlib

# ==================================================
# IMPORTS UTILIDADES
# ==================================================
from core.logger import log_line
from core.context_requirements import validate_context_for_control
from core.exceptions import AccountNotProcessableError

# ==================================================
# PATHS Y CONFIG
# ==================================================
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

with open("config/config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

active_controls = [str(cid) for cid in cfg["controls"]["controls_to_process"]]

jotlib_path = cfg["jot_lib"]["jotlib_path"]
if jotlib_path not in sys.path:
    sys.path.insert(0, jotlib_path)

# ==================================================
# IMPORTS librerías JOT
# ==================================================
from jot.jot_googleads.auth import GoogleAdsAuth # type: ignore
from jot.jot_googleads.services.gaql import GAQLService # type: ignore
from jot.jot_encrypter.jot_encrypter import JOTIM_Encrypter # type: ignore
from jot.jot_sqlserver.jot_sqlserver import SqlServerJOT # type: ignore

# ==================================================
# IMPORTS PROYECTO
# ==================================================
from SQL_catalogs_v3 import load_sql_catalogs, load_tracking_templates_catalog
from context_builder_v3 import get_account_data, build_account_context
from rules.tipo_landing_rules import resolve_tipo_landing
from resume.checkpoint import (
    get_checkpoint_path,
    load_processed_ids,
    init_checkpoint,
    append_checkpoint_row,
)
from input_sources.resolver import resolve_customer_ids


# ==================================================
# CONTEXTO BASE
# ==================================================
def build_initial_context() -> dict:
    return {
        "execution": {},
        "environment": {},
        "config": cfg,
        "input": {},
        "account": {},
        "controls": {},
        "active_controls": {},
        "services": {},
        "runtime": {},
        "cache": {},
        "tracking_catalog": {},
    }


# ==================================================
# CONTROLES
# ==================================================
def load_controls(allowed_controls: set[str]) -> dict:

    with open("config/controls.json", "r", encoding="utf-8") as f:
        controls_cfg = json.load(f)

    control_map = {}

    for c in controls_cfg:

        cid = str(c["control_id"])

        if cid not in allowed_controls:
            continue

        module_name = c["control_script"].replace("/", ".").replace(".py", "")

        module = importlib.import_module(module_name)

        control_map[cid] = {"func": module.run}

    return control_map


# ==================================================
# AGREGADOS OUTPUT
# ==================================================
def init_account_agg(user: str, customer_id: str) -> dict:

    return {
        "execution_user": user,
        "customer_id": customer_id,
        "customer_name": None,
        "has_error_funcional": False,
        "has_error_tecnico": False,
        "errores_funcionales": [],
        "errores_tecnicos": [],
        "controls_executed": 0,
    }


def update_account_agg(acc: dict, result: dict):

    acc["controls_executed"] += 1

    cid = str(result.get("control_id"))
    status = result.get("status")

    if status == "ERROR":

        acc["has_error_funcional"] = True

        acc["errores_funcionales"].append(
            {
                "control_id": cid,
                "detail": result.get("detalle"),
                "valor_esperado": result.get("valor_esperado"),
                "valor_encontrado": result.get("valor_encontrado"),
            }
        )

    elif status == "ERROR_TECNICO":

        acc["has_error_tecnico"] = True

        acc["errores_tecnicos"].append(
            {"control_id": cid, "error_tecnico": result.get("error_tecnico")}
        )


def compute_status_global(acc: dict) -> str:

    if acc["has_error_tecnico"]:
        return "ERROR_TECNICO"

    if acc["has_error_funcional"]:
        return "ERROR"

    return "OK"


def build_resumen_row(acc: dict) -> dict:

    control_ids = (
        [e["control_id"] for e in acc["errores_funcionales"]]
        + [e["control_id"] for e in acc["errores_tecnicos"]]
    )

    return {
        "execution_user": acc["execution_user"],
        "customer_id": acc["customer_id"],
        "customer_name": acc["customer_name"],
        "status_global": compute_status_global(acc),
        "controles_error": "/".join(f"C{cid}" for cid in control_ids),
        "error_tecnico": " | ".join(
            f"C{e['control_id']}: {e['error_tecnico']}"
            for e in acc["errores_tecnicos"]
            if e.get("error_tecnico")
        ),
    }


def build_detalle_rows(acc: dict) -> list[dict]:

    return [
        {
            "execution_user": acc["execution_user"],
            "customer_id": acc["customer_id"],
            "customer_name": acc["customer_name"],
            "control_id": e["control_id"],
            "status": "ERROR",
            "valor_esperado": e.get("valor_esperado"),
            "valor_encontrado": e.get("valor_encontrado"),
            "detalle": e["detail"],
        }
        for e in acc["errores_funcionales"]
    ]


# ==================================================
# MAIN
# ==================================================
def main():

    context = build_initial_context()

    execution_date = datetime.datetime.now()

    run_id = execution_date.strftime("%Y%m%d_%H%M%S")

    user = getpass.getuser()
    hostname = socket.gethostname()

    context["execution"] = {
        "run_id": run_id,
        "execution_date": execution_date,
    }

    context["environment"] = {
        "execution_user": user,
        "execution_host": hostname,
    }

    os.makedirs("logs", exist_ok=True)

    log_path = f"logs/log_{run_id}.txt"

    log_file = open(log_path, "w", encoding="utf-8")

    log_line(log_file, "INFO", f"Inicio proceso | run_id={run_id} | user={user} | host={hostname}")
    log_line(log_file, "INFO", f"Active controls: {', '.join(active_controls)}")

    execution_incompleta = False

    cuentas_ok = 0
    cuentas_error = 0
    cuentas_error_tecnico = 0

    accounts_agg = {}

    try:

        auth = GoogleAdsAuth(module_path=os.path.join(jotlib_path, "jot", "jot_googleads"))
        client = auth.get_client()
        gaql = GAQLService(client)
        context["services"]["google_ads"] = gaql

        enc = JOTIM_Encrypter()
        #(Credenciales de acceso a SQL vacías)
        conn_str = enc.Decrypt(enc._config[""][""])
        sql = SqlServerJOT(conn_str)

        context["services"]["sql_server"] = sql
        context["cache"] = load_sql_catalogs(sql)
        context["tracking_catalog"] = load_tracking_templates_catalog(sql)

        customer_ids = resolve_customer_ids(
            cfg=cfg,
            services=context["services"],
            log_file=log_file,
        )

        control_map = load_controls(set(active_controls))

        cuentas_totales = len(customer_ids)
        cuentas_procesadas = 0
        PORC_SALTO = 2
        ultimo_porc_reportado = 0

        log_line(log_file, "INFO", f"Cuentas a procesar: {cuentas_totales}")

        for customer_id in customer_ids:

            context["input"] = {"customer_id": customer_id}

            acc = init_account_agg(user, customer_id)
            accounts_agg[customer_id] = acc

            try:

                account_data = get_account_data(gaql, customer_id)
                acc["customer_name"] = account_data.get("customer_name")

                build_account_context(context, customer_id)

                control_1 = control_map["1"]
                result_1 = control_1["func"](context)
                update_account_agg(acc, result_1)

                account = context["account"]

                account["tipo_landing"] = resolve_tipo_landing(
                    socio=account.get("socio"),
                    canal=account.get("canal_compra"),
                    config_geo=account.get("config_geo"),
                )

                for cid, control in control_map.items():

                    if cid == "1":
                        continue

                    missing = validate_context_for_control(context, cid)

                    if missing:

                        result = {
                            "control_id": cid,
                            "status": "ERROR_TECNICO",
                            "error_tecnico": f"Falta de contexto: {missing}",
                        }

                    else:

                        result = control["func"](context)

                    update_account_agg(acc, result)

                status = compute_status_global(acc)

                if status == "OK":
                    cuentas_ok += 1
                elif status == "ERROR":
                    cuentas_error += 1
                else:
                    cuentas_error_tecnico += 1

                cuentas_procesadas += 1

                porcentaje = (cuentas_procesadas / cuentas_totales) * 100

                if porcentaje - ultimo_porc_reportado >= PORC_SALTO or cuentas_procesadas == cuentas_totales:

                    print(
                        f"[PROGRESS] {cuentas_procesadas}/{cuentas_totales} cuentas procesadas "
                        f"({porcentaje:.2f}%)"
                    )

                    ultimo_porc_reportado = porcentaje

            except Exception as e:

                cuentas_error_tecnico += 1

                log_line(
                    log_file,
                    "ERROR",
                    f"Error técnico cuenta | {type(e).__name__} | {e}",
                    customer_id,
                )

                continue

    except Exception as e:

        execution_incompleta = True

        log_line(log_file, "ERROR", str(e))

    suffix = "_INCOMPLETO" if execution_incompleta else ""

    os.makedirs("output/resumen", exist_ok=True)
    os.makedirs("output/errores", exist_ok=True)

    resumen_path = f"output/resumen/output_resumen_ctas{suffix}_{run_id}.csv"
    detalle_path = f"output/errores/output_errores_ctas{suffix}_{run_id}.csv"

    with open(resumen_path, "w", newline="", encoding="utf-8-sig") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "execution_user",
                "customer_id",
                "customer_name",
                "status_global",
                "controles_error",
                "error_tecnico",
            ],
            delimiter=";",
        )

        writer.writeheader()

        for acc in accounts_agg.values():
            writer.writerow(build_resumen_row(acc))

    with open(detalle_path, "w", newline="", encoding="utf-8-sig") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "execution_user",
                "customer_id",
                "customer_name",
                "control_id",
                "status",
                "valor_esperado",
                "valor_encontrado",
                "detalle",
            ],
            delimiter=";",
        )

        writer.writeheader()

        for acc in accounts_agg.values():
            for row in build_detalle_rows(acc):
                writer.writerow(row)

    log_line(
        log_file,
        "INFO",
        f"Resumen ejecución | OK={cuentas_ok} | ERROR={cuentas_error} | ERROR_TECNICO={cuentas_error_tecnico}",
    )

    log_line(log_file, "INFO", f"Output resumen: {resumen_path}")
    log_line(log_file, "INFO", f"Output detalle: {detalle_path}")

    duration = datetime.datetime.now() - execution_date
    log_line(log_file, "INFO", f"Duración proceso: {duration}")
    log_line(log_file, "INFO", "Fin proceso")

    log_file.close()


if __name__ == "__main__":
    main()