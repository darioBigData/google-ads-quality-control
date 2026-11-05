"""
Naming Parser - QC Ads

Responsabilidades:
- Extraer atributos de negocio desde naming conventions.
- NO contener lógica de validación de negocio.
- Ser reutilizable por context_builder u otros módulos.
"""


def extract_pais_idioma_from_campaign(campaign_name: str) -> tuple:
    """
    Extrae país e idioma desde el nombre de campaña.

    Regla:
    - Formato esperado: <PAIS>_<IDIOMA>_...
    
    Ejemplo:
    AUS_EN_00_... → ("AUS", "EN")
    """

    if not campaign_name:
        raise Exception("CAMPAIGN_NAME_EMPTY")

    parts = campaign_name.split("_")

    if len(parts) < 2:
        raise Exception(f"INVALID_CAMPAIGN_NAMING | campaign_name={campaign_name}")

    pais = parts[0].strip().upper()
    idioma = parts[1].strip().upper()

    if not pais or not idioma:
        raise Exception(f"INVALID_CAMPAIGN_VALUES | campaign_name={campaign_name}")

    return pais, idioma


def extract_destino_from_account(account_name: str) -> str:
    """
    Extrae el destino desde el nombre de la cuenta.

    Regla:
    - El destino es el penúltimo bloque separado por "_"
    
    Ejemplo:
    DNK_HKD_005_P_A_SC_JOT_EDU_100 → EDU
    """

    if not account_name:
        raise Exception("ACCOUNT_NAME_EMPTY")

    parts = account_name.split("_")

    if len(parts) < 2:
        raise Exception(f"INVALID_ACCOUNT_NAMING | account_name={account_name}")

    destino = parts[-2].strip().upper()

    if not destino:
        raise Exception(f"INVALID_DESTINO | account_name={account_name}")

    return destino