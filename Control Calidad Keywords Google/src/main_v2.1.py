import os
import sys
import json
import logging
from datetime import datetime

# =========================
# PATH BASE
# =========================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# =========================
# IMPORTS
# =========================
from core.control_loader import load_controls
from core.checkpoint_manager import CheckpointManager
from core.control_validator import validate_control_result
from context.context_builder import build_contexts
from output.aggregator import build_output_rows
from output.output_writer import write_outputs


# =========================
# LOGGER
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# =========================
# HELPERS
# =========================
def build_campaign_key(context):
    return f"{str(context.get('customer_id'))}|{str(context.get('campaign_id'))}"


def execute_controls(context, controls):
    results = []

    for control in controls:

        if control["entity_type"] != context.get("entity_type"):
            continue

        try:
            result = control["run"]({"entity": context})

            # Asegurar campos
            result["control_name"] = control["control_name"]
            result.setdefault("error_tecnico", False)

            validate_control_result(result)

        except Exception as e:
            results.append({
                "control_id": control["control_id"],
                "control_name": control["control_name"],
                "status": "ERROR_TECNICO",
                "valor_esperado": None,
                "valor_encontrado": None,
                "detalle": str(e),
                "error_tecnico": True
            })

    return results


# =========================
# MAIN
# =========================
def main():

    # =========================
    # CONFIG
    # =========================
    with open("config/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    execution_user = os.getlogin()
    process_cfg = config.get("process", {})
    run_id_reference = process_cfg.get("run_id_reference")

    if run_id_reference:
        run_id = str(run_id_reference).strip()
        logging.info(f"[RUN] Reutilizando run_id: {run_id}")
    else:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        logging.info(f"[RUN] Nuevo run_id generado: {run_id}")

    logging.info(f"Inicio proceso | run_id={run_id} | user={execution_user}")

    # =========================
    # CHECKPOINT
    # =========================
    checkpoint_path = os.path.join(
        config["paths"]["checkpoint_dir"],
        f"checkpoint_{run_id}.json"
    )

    checkpoint = CheckpointManager(checkpoint_path)

    logging.info(f"Checkpoint file: {checkpoint_path}")

    try:

        # =========================
        # LOAD CONTROLS
        # =========================
        controls = load_controls("config/controls.json")

        # =========================
        # BUILD CONTEXTS
        # =========================
        contexts = build_contexts(config)

        if not contexts:
            logging.warning("No hay entidades para procesar")
            return

        # =========================
        # AGRUPAR POR CAMPAÑA
        # =========================
        campaign_groups = {}

        for context in contexts:
            key = build_campaign_key(context)
            campaign_groups.setdefault(key, []).append(context)

        total_campaigns = len(campaign_groups)
        logging.info(f"Total campañas a procesar: {total_campaigns}")

        # =========================
        # EJECUCIÓN
        # =========================
        all_results = []
        processed_campaigns = 0

        for campaign_key, entities in campaign_groups.items():

            if checkpoint.has_processed(campaign_key):
                logging.info(f"[CHECKPOINT] Skip campaña: {campaign_key}")
                continue

            processed_campaigns += 1

            logging.info(f"[PROCESS] Campaign: {campaign_key}")
            logging.info(f"[INFO] Entidades en campaña: {len(entities)}")

            campaign_failed = False
            campaign_results = []

            for context in entities:

                try:
                    results = execute_controls(context, controls)

                    campaign_results.append({
                        "entity": context,
                        "results": results
                    })

                except Exception as e:
                    campaign_failed = True

                    campaign_results.append({
                        "entity": context,
                        "results": [],
                        "entity_tech_error": True
                    })

            # =========================
            # CHECKPOINT SOLO SI OK
            # =========================
            if not campaign_failed:
                checkpoint.mark_processed(campaign_key)
                logging.info(f"[CHECKPOINT] OK campaña: {campaign_key}")
            else:
                logging.warning(f"[CHECKPOINT] NO guardado (error): {campaign_key}")

            all_results.extend(campaign_results)

            progress_pct = (
                round(processed_campaigns / total_campaigns * 100, 2)
                if total_campaigns > 0 else 0
            )

            logging.info(
                f"[PROGRESS] {processed_campaigns}/{total_campaigns} campañas ({progress_pct}%)"
            )

        # =========================
        # OUTPUT
        # =========================
        summary_rows, error_rows = build_output_rows(
            all_results,
            execution_user=execution_user
        )

        write_outputs(
            summary_rows=summary_rows,
            error_rows=error_rows,
            config=config,
            run_id=run_id
        )

        logging.info("Proceso finalizado correctamente")

    except Exception as e:
        logging.error(f"FATAL | {str(e)}", exc_info=True)


# =========================
# ENTRYPOINT
# =========================
if __name__ == "__main__":
    main()