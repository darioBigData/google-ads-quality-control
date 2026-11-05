# ============================================
# CONTROL 5 — Tracking Template (SQL-aligned)
# Fuente de verdad: TrackingTemplates_LineaDeNegocio (Google)
# ============================================

def run(context: dict) -> dict:
    control_id = "5"

    account = context.get("account", {})
    tracking_catalog = context.get("tracking_catalog", {})

    tracking_cuenta = account.get("tracking_template")
    socio = account.get("socio")
    destino = account.get("destino")         
    tipo_landing = account.get("tipo_landing")
    canal = account.get("canal_compra").strip().upper()


    # --- Validación de contexto mínimo (defensiva) ---
    if canal != "DEMGEN" and not all([socio, destino, tipo_landing, canal]):
        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": "Contexto completo (socio, destino, tipo_landing, canal)",
            "valor_encontrado": f"socio={socio}, destino={destino}, tipo_landing={tipo_landing}, canal={canal}",
            "detalle": "Falta contexto mínimo para validar tracking template",
            "error_tecnico": "Falta de contexto",
        }
    
    if canal == "DEMGEN":
        return {
            "control_id": control_id,
            "status": "OK",
            "valor_esperado": "Sin tracking template (DG)",
            "valor_encontrado": tracking_cuenta,
            "detalle": "Las cuentas Demand Gen no requieren tracking template",
            "error_tecnico": None,
        }    

    # --- Construcción CLAVE_CONCAT (sin Origen) ---
    clave_concat = "_".join([
        socio.upper().strip(),
        destino.upper().strip(),
        tipo_landing.upper().strip(),
        canal.upper().strip(),
    ])

    """
    print(
    f"[DEBUG][CONTROL_5][CLAVE_CONCAT] "
    f"customer_id={account.get('customer_id')} | "
    f"clave={clave_concat}"
    )
    """
    tracking_control = tracking_catalog.get(clave_concat)

    # --- SIN DEFINICIÓN = ERROR ---
    if tracking_control is None:
        return {
            "control_id": control_id,
            "status": "ERROR",  
            "valor_esperado": "Definición existente en catálogo",
            "valor_encontrado": None,
            "detalle": "No existe definición de tracking para esta combinación",
            "error_tecnico": None,
        }

    if tracking_cuenta is None:
        return {
            "control_id": control_id,
            "status": "ERROR",
            "valor_esperado": tracking_control,
            "valor_encontrado": None,
            "detalle": "La cuenta no tiene tracking template configurado",
            "error_tecnico": None,
        }

    tracking_cuenta_norm = tracking_cuenta.strip()
    tracking_control_norm = tracking_control.strip()

    if tracking_cuenta_norm == tracking_control_norm:
        return {
            "control_id": control_id,
            "status": "OK",
            "valor_esperado": tracking_control_norm,
            "valor_encontrado": tracking_cuenta_norm,
            "detalle": "El tracking template coincide exactamente con el catálogo",
            "error_tecnico": None,
        }

    # --- TRACKING INCORRECTO ---
    return {
        "control_id": control_id,
        "status": "ERROR",
        "valor_esperado": tracking_control_norm,
        "valor_encontrado": tracking_cuenta_norm,
        "detalle": "El tracking template no coincide con el definido en catálogo",
        "error_tecnico": None,
    }
