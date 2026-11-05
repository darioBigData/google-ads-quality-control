import getpass
import json
import os
import sys
import time
import traceback
from datetime import datetime
from typing import Dict, List

from context.context_builder import build_contexts
from context.SQL_catalogs import load_all_catalogs
from core.checkpoint_manager_v2 import CheckpointManager
from core.control_loader import load_controls
from core.control_validator import validate_control_result
from core.logger import ProcessLogger
from input_providers.csv_input_provider import CsvInputProvider
from output.aggregator import build_errores_rows, build_resumen_row
from output.output_writer import OutputWriter
from utils.jotlib_loader import ensure_jotlib_on_path


def load_config() -> Dict:
    with open(os.path.join("config", "config.json"), "r", encoding="utf-8") as file:
        return json.load(file)


def ensure_directories(cfg: Dict) -> None:
    os.makedirs(cfg["log_folder"], exist_ok=True)
    os.makedirs(cfg["output"]["resumen_folder"], exist_ok=True)
    os.makedirs(cfg["output"]["errores_folder"], exist_ok=True)
    if cfg["resume"]["enabled"]:
        os.makedirs(cfg["resume"]["checkpoint_folder"], exist_ok=True)


def build_run_id(cfg: Dict, logger: ProcessLogger) -> str:
    run_id_reference = cfg.get("resume", {}).get("run_id_reference")

    if run_id_reference:
        logger.info(f"[RUN] Reanudando ejecución con run_id: {run_id_reference}")
        return str(run_id_reference).strip()

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.info(f"[RUN] Nuevo run_id generado: {run_id}")
    return run_id


def build_checkpoint_file(cfg: Dict, run_id: str) -> str:
    folder = cfg["resume"]["checkpoint_folder"]
    prefix = cfg["resume"]["checkpoint_prefix"]
    return os.path.join(folder, f"{prefix}_{run_id}.json")


def build_ad_key(context: Dict) -> str:
    return "|".join([
        str(context.get("customer_id", "")),
        str(context.get("ad_group_id", "")),
        str(context.get("ad_id", ""))
    ])


def execute_controls(context: Dict, controls: List[Dict], logger: ProcessLogger) -> List[Dict]:
    results = []

    for control in controls:
        try:
            result = control["run"](context, control.get("params", {}))

            result["control_id"] = control["control_id"]
            result["control_name"] = control["control_name"]

            validate_control_result(result)

            results.append(result)

        except Exception as exc:
            logger.error(
                f"Fallo técnico en control {control['control_id']} "
                f"sobre ad_id={context.get('ad_id')}: {exc}"
            )

            results.append({
                "control_id": control["control_id"],
                "control_name": control["control_name"],
                "status": "ERROR_TECNICO",
                "severity": "",
                "valor_esperado": "",
                "valor_encontrado": "",
                "detalle": "Fallo técnico durante la ejecución del control.",
                "error_tecnico": str(exc)
            })

    return results


def main() -> None:
    cfg = load_config()
    ensure_directories(cfg)

    logger = ProcessLogger(cfg["log_folder"], cfg.get("log_level", "normal"))
    run_id = build_run_id(cfg, logger)
    execution_user = getpass.getuser() if cfg.get("register_user", True) else ""

    logger.info("Inicio del proceso QC Ads.")
    logger.info(f"Usuario de ejecución: {execution_user}")
    logger.info(f"Run interno: {run_id}")

    checkpoint_file = build_checkpoint_file(cfg, run_id)
    checkpoint_manager = CheckpointManager(checkpoint_file)

    logger.info(f"Checkpoint activo: {checkpoint_file}")
    logger.info(f"Ads ya procesados (checkpoint): {checkpoint_manager.get_processed_count()}")

    # --- INPUT ---
    input_provider = CsvInputProvider(
        file_path=cfg["input_file"],
        delimiter=cfg.get("input_delimiter", ";")
    )

    input_rows = input_provider.read_rows(cfg["limits"]["max_rows_per_execution"])
    logger.info(f"Filas leídas del input: {len(input_rows)}")

    # --- CONTROLES ---
    controls = load_controls(cfg["controls_file"])

    controls_to_process = cfg.get("controls", {}).get("controls_to_process")
    if controls_to_process:
        controls_to_process = set(str(c) for c in controls_to_process)
        controls = [c for c in controls if str(c["control_id"]) in controls_to_process]

    logger.info(f"Controles activos: {len(controls)}")

    # --- JOT LIB ---
    jotlib_path = cfg.get("paths", {}).get("jotlib_path")
    ensure_jotlib_on_path(jotlib_path)

    from jot.jot_googleads.auth import GoogleAdsAuth  # type: ignore
    from jot.jot_googleads.services.gaql import GAQLService  # type: ignore
    from jot.jot_encrypter.jot_encrypter import JOTIM_Encrypter  # type: ignore
    from jot.jot_sqlserver.jot_sqlserver import SqlServerJOT  # type: ignore

    # GOOGLE ADS
    auth = GoogleAdsAuth(
        module_path=os.path.join(jotlib_path, "jot", "jot_googleads")
    )
    client = auth.get_client()
    gaql = GAQLService(client)

    # SQL
    enc = JOTIM_Encrypter()
    #(Credenciales de acceso a SQL vacías)
    conn_str = enc.Decrypt(enc._config[""][""])
    sql = SqlServerJOT(conn_str)

    catalogs = load_all_catalogs(sql)

    writer = OutputWriter(
        resumen_folder=cfg["output"]["resumen_folder"],
        errores_folder=cfg["output"]["errores_folder"],
        delimiter=cfg.get("input_delimiter", ";")
    )

    # =========================
    # FASE 1: RECUPERAR ADS
    # =========================

    all_contexts = []
    metrics = {"total_calls": 0}

    for input_row in input_rows:
        contexts = build_contexts(gaql, input_row, metrics)
        all_contexts.extend(contexts)

    logger.info(f"Ads recuperados totales: {len(all_contexts)}")

    # =========================
    # FASE 2: DEDUPE
    # =========================

    unique = {}
    for ctx in all_contexts:
        key = build_ad_key(ctx)
        if key not in unique:
            unique[key] = ctx

    final_contexts = list(unique.values())

    logger.info(f"Ads tras deduplicación: {len(final_contexts)}")

    # =========================
    # FASE 3: PROCESAMIENTO
    # =========================

    resumen_rows = []
    errores_rows = []

    total_ads = len(final_contexts)
    processed_ads = checkpoint_manager.get_processed_count()

    PORC_SALTO = 2
    ultimo_porc = 0

    retry_cfg = cfg.get("retries", {})
    retry_enabled = retry_cfg.get("enabled", True)
    max_attempts = int(retry_cfg.get("max_attempts", 3))
    base_delay = int(retry_cfg.get("base_delay_seconds", 2))

    for context in final_contexts:

        context["catalogs"] = catalogs
        ad_key = build_ad_key(context)

        if checkpoint_manager.has_processed(ad_key):
            continue

        attempt = 0
        success = False
        last_exception = None

        while True:
            attempt += 1

            try:
                control_results = execute_controls(context, controls, logger)

                resumen_rows.append(
                    build_resumen_row(
                        context=context,
                        control_results=control_results,
                        execution_user=execution_user
                        #checkpoint_status="PROCESSED"
                    )
                )

                errores_rows.extend(
                    build_errores_rows(
                        context=context,
                        control_results=control_results,
                        execution_user=execution_user
                    )
                )

                checkpoint_manager.mark_processed(ad_key)
                success = True
                break

            except Exception as e:
                last_exception = e
                logger.error(f"RETRY {attempt}/{max_attempts} | ad_key={ad_key} | {e}")

                # recrear cliente GA
                auth = GoogleAdsAuth(
                    module_path=os.path.join(jotlib_path, "jot", "jot_googleads")
                )
                client = auth.get_client()
                gaql = GAQLService(client)

                if not retry_enabled or attempt >= max_attempts:
                    break

                time.sleep(base_delay * attempt)

        if not success:
            resumen_rows.append(
                build_resumen_row(
                    context=context,
                    control_results=[],
                    execution_user=execution_user
                    #checkpoint_status="ERROR"
                )
            )

            checkpoint_manager.mark_processed(ad_key)

        processed_ads += 1

        if total_ads > 0:
            porcentaje = (processed_ads / total_ads) * 100

            if porcentaje - ultimo_porc >= PORC_SALTO or processed_ads == total_ads:
                print(
                    f"[PROGRESS] {processed_ads}/{total_ads} anuncios procesados ({porcentaje:.2f}%)"
                )
                ultimo_porc = porcentaje

    # =========================
    # OUTPUT FINAL
    # =========================

    writer.write_resumen(resumen_rows, cfg["output_fields"]["resumen"])
    writer.write_errores(errores_rows, cfg["output_fields"]["errores"])

    logger.info(f"Ads procesados: {processed_ads}")
    logger.info(f"Llamadas GAQL: {metrics['total_calls']}")

    # borrar checkpoint si completado
    if processed_ads >= total_ads:
        checkpoint_manager.delete()
        logger.info("Checkpoint eliminado (proceso completo)")

    logger.info("Proceso finalizado correctamente.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        fallback_log = ProcessLogger("logs", "normal")
        fallback_log.error(f"Fallo fatal del proceso: {exc}")
        fallback_log.error(traceback.format_exc())
        raise