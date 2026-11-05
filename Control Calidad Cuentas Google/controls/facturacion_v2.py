def run(context: dict) -> dict:
    """
    Control 10 – Cuenta de Facturación (Billing JOT)

    Valida que la cuenta tenga como billing activo
    una cuenta de facturación JOT permitida.

    Principios:
    - El billing activo ya viene decidido en el main
    - Este control NO selecciona billing
    - Este control SOLO evalúa contexto
    """

    control_id = "10"

    # Payments Account JOT permitido (normalizado)
    JOT_PAYMENTS_ACCOUNT_ID = "3346-5368-2267-7514"

    billing = context.get("billing")

    # --- VALIDACIÓN DE CONTEXTO ---
    if billing is None:
        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": JOT_PAYMENTS_ACCOUNT_ID,
            "valor_encontrado": None,
            "detalle": "Contexto de billing no disponible",
            "error_tecnico": "context['billing'] es None"
        }

    if billing.get("error_tecnico"):
        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": JOT_PAYMENTS_ACCOUNT_ID,
            "valor_encontrado": None,
            "detalle": "Error tecnico en resolución de billing activo",
            "error_tecnico": billing.get("error_tecnico")
        }

    active_billing = billing.get("active_billing_setup")

    # --- NO HAY BILLING ACTIVO ---
    if active_billing is None:
        return {
            "control_id": control_id,
            "status": "ERROR",
            "valor_esperado": JOT_PAYMENTS_ACCOUNT_ID,
            "valor_encontrado": None,
            "detalle": "La cuenta no tiene un billing activo definido",
            "error_tecnico": None
        }

    # --- VALIDACIÓN DEL PAYMENTS ACCOUNT ---
    payments_account = active_billing.get("payments_account")

    if not payments_account:
        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": JOT_PAYMENTS_ACCOUNT_ID,
            "valor_encontrado": None,
            "detalle": "Billing activo sin payments_account",
            "error_tecnico": "payments_account vacio en active_billing_setup"
        }

    # Normalización robusta del payments_account
    payments_account_norm = str(payments_account).strip().split("/")[-1]

    # --- VALIDACIÓN FINAL ---
    if payments_account_norm == JOT_PAYMENTS_ACCOUNT_ID:
        return {
            "control_id": control_id,
            "status": "OK",
            "valor_esperado": JOT_PAYMENTS_ACCOUNT_ID,
            "valor_encontrado": payments_account_norm,
            "detalle": "La cuenta tiene como billing activo la facturacion JOT permitida (3346-...)",
            "error_tecnico": None
        }

    return {
        "control_id": control_id,
        "status": "ERROR",
        "valor_esperado": JOT_PAYMENTS_ACCOUNT_ID,
        "valor_encontrado": payments_account_norm,
        "detalle": "El billing activo de la cuenta no corresponde a una facturacion JOT permitida",
        "error_tecnico": None
    }
