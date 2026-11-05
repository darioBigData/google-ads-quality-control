import os
import sys
import json
import time
import getpass
import importlib.util
from datetime import datetime

from context.context_builder_v0 import build_adgroup_contexts
from checkpoint.checkpoint_manager import load_checkpoint, add_processed_id

from output.aggregator import aggregate_results
from output.output_writer import write_outputs

from core.logger import create_logger, log_info, log_error


# ---------------------------------------------------------
# UTILIDADES
# ---------------------------------------------------------
def generate_run_id():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def load_json(path):
    if not os.path.isfile(path):
        raise Exception(f"Archivo no encontrado: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_control_module(control_path):

    if not os.path.isfile(control_path):
        raise Exception(f"Control no encontrado: {control_path}")

    module_name = os.path.basename(control_path).replace(".py", "")

    spec = importlib.util.spec_from_file_location(module_name, control_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def print_progress(current, total, last_printed_pct):

    if total == 0:
        return last_printed_pct

    pct = (current / total) * 100

    if int(pct // 2) > last_printed_pct:

        print(f"[PROGRESS] {current}/{total} ad groups procesados ({pct:.2f}%)")

        return int(pct // 2)

    return last_printed_pct


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():

    print("MAIN ARRANCADO\n")

    start_time = time.time()

    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # ---------------------------------------------------------
    # CONFIG
    # ---------------------------------------------------------
    config_path = os.path.join(BASE_DIR, "config", "config.json")
    config = load_json(config_path)

    controls_config_path = os.path.join(BASE_DIR, "config", "controls.json")
    controls_config = load_json(controls_config_path)

    # ---------------------------------------------------------
    # RUN ID
    # ---------------------------------------------------------
    run_id_reference = config.get("process", {}).get("run_id_reference")

    if run_id_reference:
        execution_id = str(run_id_reference).strip()
        print(f"[RUN] Reutilizando run_id: {execution_id}")
    else:
        execution_id = generate_run_id()
        print(f"[RUN] Nuevo run_id generado: {execution_id}")

    execution_user = getpass.getuser()

    # ---------------------------------------------------------
    # LOGGER
    # ---------------------------------------------------------
    logs_dir = os.path.join(BASE_DIR, config["paths"]["logs"])

    logger = create_logger(
        logs_dir=logs_dir,
        run_id=execution_id
    )

    log_info(logger, f"Inicio proceso | run_id={execution_id} | user={execution_user}")

    # ---------------------------------------------------------
    # JOT LIB PATH
    # ---------------------------------------------------------
    jotlib_path = config.get("paths", {}).get("jotlib_path")

    if jotlib_path and jotlib_path not in sys.path:
        sys.path.insert(0, jotlib_path)

    # ---------------------------------------------------------
    # IMPORT GAQL
    # ---------------------------------------------------------
    try:
        from jot.jot_googleads.auth import GoogleAdsAuth # type: ignore
        from jot.jot_googleads.services.gaql import GAQLService # type: ignore

        auth = GoogleAdsAuth(
            module_path=os.path.join(jotlib_path, "jot", "jot_googleads")
        )

        client = auth.get_client()
        gaql = GAQLService(client)

        log_info(logger, "GAQL inicializado correctamente")

    except Exception as e:
        log_error(logger, f"Error inicializando GAQL: {e}")
        raise

    # ---------------------------------------------------------
    # CHECKPOINT
    # ---------------------------------------------------------
    checkpoint_data = load_checkpoint(execution_id)
    processed_ids = checkpoint_data["processed_ids_set"]

    log_info(logger, f"Checkpoint cargado: {len(processed_ids)} ad groups ya procesados")

    # ---------------------------------------------------------
    # INPUT
    # ---------------------------------------------------------
    input_path = os.path.join(BASE_DIR, config["paths"]["input"])

    if not os.path.isfile(input_path):
        raise Exception(f"Input no encontrado: {input_path}")

    import csv

    with open(input_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        input_rows = list(reader)

    log_info(logger, f"Filas CSV: {len(input_rows)}")

    # ---------------------------------------------------------
    # LOAD CONTROLS (FILTRADOS)
    # ---------------------------------------------------------
    controls_to_process = config.get("controls", {}).get("controls_to_process", [])
    controls_to_process = [str(c) for c in controls_to_process]

    control_modules = {}
    active_controls = []

    for ctrl in controls_config:

        control_id = str(ctrl.get("control_id"))
        script_path = ctrl.get("control_script")

        if controls_to_process and control_id not in controls_to_process:
            continue

        full_path = os.path.join(BASE_DIR, script_path)

        try:
            module = load_control_module(full_path)
            control_modules[control_id] = module
            active_controls.append(control_id)

        except Exception as e:
            log_error(logger, f"Error cargando control {control_id}: {e}")

    log_info(logger, f"Controles activos: {active_controls}")

    # ---------------------------------------------------------
    # CONTEXTO BASE
    # ---------------------------------------------------------
    context_base = {
        "services": {
            "google_ads": gaql
        },
        "metrics": {
            "total_calls": 0
        }
    }

    # ---------------------------------------------------------
    # BUILD CONTEXTS
    # ---------------------------------------------------------
    all_contexts = []

    for row in input_rows:

        customer_id = row.get("customer_id")
        campaign_id = row.get("campaign_id")
        ad_group_id = row.get("ad_group_id")

        if not customer_id:
            log_error(logger, "Fila sin customer_id → ignorada")
            continue

        try:

            contexts = build_adgroup_contexts(
                context=context_base,
                customer_id=customer_id,
                campaign_id=campaign_id,
                ad_group_id=ad_group_id,
                processed_ids_set=processed_ids
            )

            all_contexts.extend(contexts)

        except Exception as e:
            log_error(logger, f"Error construyendo contextos | customer={customer_id} | error={e}")

    total_adgroups = len(all_contexts)

    print(f"[RUN] Total ad groups a procesar: {total_adgroups}")
    log_info(logger, f"Total Ad Groups a procesar: {total_adgroups}")

    # ---------------------------------------------------------
    # EJECUCIÓN CONTROLES
    # ---------------------------------------------------------
    results = []
    processed_count = 0
    last_printed_pct = -1

    for ctx in all_contexts:

        customer_id = ctx.get("customer_id")
        ad_group_id = ctx["ad_group"]["ad_group_id"]

        checkpoint_key = f"{customer_id}_{ad_group_id}"

        if checkpoint_key in processed_ids:
            continue

        for control_id in active_controls:

            module = control_modules[control_id]

            try:
                result = module.run(ctx)

            except Exception as e:

                log_error(
                    logger,
                    f"Control error técnico | control={control_id} | ad_group={ad_group_id} | error={e}"
                )

                result = {
                    "control_id": control_id,
                    "status": "ERROR_TECNICO",
                    "valor_esperado": None,
                    "valor_encontrado": None,
                    "detalle": None,
                    "error_tecnico": str(e)
                }

            results.append({
                "execution_user": execution_user,
                "customer_id": ctx.get("customer_id"),
                "customer_name": ctx.get("customer_name"),
                "campaign_id": ctx.get("campaign_id"),
                "campaign_name": ctx.get("campaign_name"),
                "ad_group_id": ctx["ad_group"]["ad_group_id"],
                "ad_group_name": ctx["ad_group"]["ad_group_name"],
                **result
            })

        add_processed_id(checkpoint_data, checkpoint_key)
        processed_ids.add(checkpoint_key)

        processed_count += 1

        last_printed_pct = print_progress(
            processed_count,
            total_adgroups,
            last_printed_pct
        )

    # ---------------------------------------------------------
    # OUTPUT
    # ---------------------------------------------------------
    if results:

        try:

            resumen, errores = aggregate_results(results)

            write_outputs(
                BASE_DIR,
                resumen,
                errores,
                execution_id
            )

            log_info(logger, "Outputs generados correctamente")

        except Exception as e:
            log_error(logger, f"Error generando outputs: {e}")

    else:
        log_info(logger, "No hay resultados para generar output")

    # ---------------------------------------------------------
    # MÉTRICAS
    # ---------------------------------------------------------
    elapsed = time.time() - start_time

    total_ok = sum(1 for r in results if r.get("status") == "OK")
    total_not_ok = sum(1 for r in results if r.get("status") != "OK")

    log_info(logger, f"Nº Ad Groups procesados: {total_adgroups}")
    log_info(logger, f"Nº resultados OK: {total_ok}")
    log_info(logger, f"Nº resultados != OK: {total_not_ok}")
    log_info(logger, f"Nº llamadas Google Ads: {context_base['metrics']['total_calls']}")
    log_info(logger, f"Duración total (s): {round(elapsed, 2)}")

    print("\n[RUN] Proceso completado\n")


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------
if __name__ == "__main__":
    main()