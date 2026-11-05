import os
import sys
import json
import time
import getpass
from datetime import datetime

# --- PATH BASE PROYECTO ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# --- CONFIG ---
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")

if not os.path.isfile(CONFIG_PATH):
    raise FileNotFoundError(f"No existe config.json en: {CONFIG_PATH}")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

# --- JOT LIB ---
jotlib_path = config["paths"]["jotlib_path"]

if jotlib_path not in sys.path:
    sys.path.insert(0, jotlib_path)

from jot.jot_googleads.auth import GoogleAdsAuth  # type: ignore
from jot.jot_googleads.services.gaql import GAQLService  # type: ignore

# --- IMPORTS PROYECTO ---
from core.control_loader import load_control
from core.control_validator import run_control
from core.logger import create_logger, log_info, log_error
from core.checkpoint_manager_v2 import (
    load_checkpoint,
    add_processed_id
)
from context.context_builder_v2 import build_asset_group_contexts
from input_providers.csv_input_provider import read_input_csv
from output.aggregator import aggregate_results
from output.output_writer_v2 import write_outputs


# --- UTILIDADES ---
def run_id_compact():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# --- CONTROLES ---
def load_controls(root_path, config):

    controls_path = os.path.join(root_path, "config", "controls.json")

    with open(controls_path, "r", encoding="utf-8") as f:
        controls = json.load(f)

    controls_def_map = {c["control_id"]: c for c in controls}

    controls_to_process = config.get("controls", {}).get(
        "controls_to_process", []
    )

    active_controls = [
        cid for cid in controls_to_process
        if cid in controls_def_map
    ]

    return controls, controls_def_map, active_controls


# --- GOOGLE ADS SERVICES ---
def init_services(config):

    auth = GoogleAdsAuth(
        module_path=os.path.join(jotlib_path, "jot", "jot_googleads")
    )

    client = auth.get_client()

    gaql = GAQLService(client)

    services = {
        "google_ads": gaql
    }

    return services


# --- MAIN ---
def main():

    print("\nQC Asset Groups iniciado\n", flush=True)

    start_time = time.time()

    run_id_reference = config.get("process", {}).get("run_id_reference")

    if run_id_reference:
        execution_id = str(run_id_reference).strip()
        print(f"[RUN] Reutilizando run_id existente: {execution_id}")
    else:
        execution_id = run_id_compact()
        print(f"[RUN] Nuevo run_id generado: {execution_id}")

    execution_user = getpass.getuser()

    logs_dir = os.path.join(BASE_DIR, "logs")

    # ---------------------------------------------------------
    # CHECKPOINT (NUEVO SISTEMA)
    # ---------------------------------------------------------
    checkpoint_data = load_checkpoint(execution_id)
    processed_ids = checkpoint_data["processed_ids_set"]

    already_processed = len(processed_ids)

    print(
        f"Checkpoint cargado: {already_processed} Asset Groups ya procesados"
    )

    logger = create_logger(
        logs_dir=logs_dir,
        run_id=execution_id
    )

    if already_processed > 0:
        log_info(
            logger,
            f"Reanudación proceso | run_id={execution_id} | "
            f"{already_processed} Asset Groups ya procesados"
        )
    else:
        log_info(
            logger,
            f"Inicio proceso | run_id={execution_id} | user={execution_user}"
        )

    # SERVICES
    services = init_services(config)

    # CONTROLES
    controls, controls_def_map, active_controls = load_controls(
        BASE_DIR,
        config
    )

    log_info(
        logger,
        f"Active controls: {', '.join(active_controls)}"
    )

    control_modules = {}

    for control_id in active_controls:

        control_meta = controls_def_map[control_id]

        module = load_control(
            control_meta["control_script"]
        )

        control_modules[control_id] = module

    # CONTEXTO BASE
    context = {
        "services": services,
        "metrics": {
            "total_calls": 0
        },
        "customer_cache": {}  # 🔥 NUEVO (cache GAQL)
    }

    # INPUT
    input_rows = read_input_csv(BASE_DIR)

    log_info(logger, f"Filas CSV: {len(input_rows)}")

    results = []

    # ---------------------------------------------------------
    # BUILD CONTEXTS (CON FILTRO DE CHECKPOINT)
    # ---------------------------------------------------------
    all_ag_contexts = []

    for row in input_rows:

        customer_id = row.get("customer_id")
        campaign_id = row.get("campaign_id")

        if not customer_id:
            continue

        ag_contexts = build_asset_group_contexts(
            context=context,
            config=config,
            customer_id=customer_id,
            campaign_id=campaign_id,
            active_controls=active_controls,
            controls_def_map=controls_def_map,
            processed_ids_set=processed_ids  # 🔥 CLAVE
        )

        all_ag_contexts.extend(ag_contexts)

    total_asset_groups = len(all_ag_contexts)

    print(f"Total Asset Groups a procesar: {total_asset_groups}\n")

    # LOOP PRINCIPAL
    processed_this_run = 0
    already_processed = len(processed_ids)

    PORC_SALTO = 2
    ultimo_porc_reportado = (already_processed / total_asset_groups) * 100 if total_asset_groups else 0

    interrupted = False

    try:

        for ag_context in all_ag_contexts:

            customer_id = ag_context.get("customer_id")
            asset_group_id = ag_context["asset_group"]["asset_group_id"]

            checkpoint_key = f"{customer_id}_{asset_group_id}"

            # 🔥 ya no debería ocurrir, pero mantenemos seguridad
            if checkpoint_key in processed_ids:
                continue

            processed_this_run += 1

            current_total = already_processed + processed_this_run

            porcentaje = (current_total / total_asset_groups) * 100 if total_asset_groups else 0

            if (
                porcentaje - ultimo_porc_reportado >= PORC_SALTO
                or current_total == total_asset_groups
            ):
                print(
                    f"[PROGRESS] {current_total}/{total_asset_groups} "
                    f"Asset Groups procesados ({porcentaje:.2f}%)",
                    flush=True
                )
                ultimo_porc_reportado = porcentaje

            for control_id in active_controls:

                module = control_modules[control_id]

                try:
                    result = run_control(
                        module,
                        ag_context
                    )

                except Exception as e:

                    log_error(
                        logger,
                        f"Control {control_id} error técnico: {str(e)}"
                    )

                    result = {
                        "control_id": control_id,
                        "status": "ERROR_TECNICO",
                        "valor_esperado": "",
                        "valor_encontrado": "",
                        "detalle": "",
                        "error_tecnico": str(e)
                    }

                results.append(result)

            # -------------------------------------------------
            # CHECKPOINT (APPEND-ONLY 🔥)
            # -------------------------------------------------
            add_processed_id(checkpoint_data, checkpoint_key)

            processed_ids.add(checkpoint_key)

    except KeyboardInterrupt:

        interrupted = True

        print("\n\nProceso interrumpido por el usuario.")

    # -------- OUTPUTS --------
    aggregated = aggregate_results(results)

    suffix = ""

    if interrupted:
        suffix = "_INCOMPLETO"

    write_outputs(
        BASE_DIR,
        aggregated,
        execution_id,
        suffix=suffix
    )

    # -------- MÉTRICAS --------
    total_calls = context["metrics"]["total_calls"]

    total_ok = sum(
        1 for r in results
        if r.get("status") == "OK"
    )

    total_not_ok = sum(
        1 for r in results
        if r.get("status") != "OK"
    )

    end_time = time.time()

    duration = round(end_time - start_time, 2)

    calls_per_ag = round(
        total_calls / total_asset_groups,
        4
    ) if total_asset_groups else 0

    calls_per_min = round(
        (total_calls / duration) * 60,
        4
    ) if duration else 0

    log_info(logger, f"Nº Asset Groups procesados: {total_asset_groups}")
    log_info(logger, f"Nº resultados OK: {total_ok}")
    log_info(logger, f"Nº resultados != OK: {total_not_ok}")
    log_info(logger, f"Nº llamadas Google Ads: {total_calls}")
    log_info(logger, f"Media llamadas por AG: {calls_per_ag}")
    log_info(logger, f"Llamadas por minuto: {calls_per_min}")
    log_info(logger, f"Duración total (s): {duration}")


if __name__ == "__main__":
    main()