from typing import Dict, List

from context.data.ad_data import get_ads_by_scope
from utils.naming_parser import (
    extract_pais_idioma_from_campaign,
    extract_destino_from_account
)


def build_contexts(gaql, input_row: dict, metrics: dict) -> List[Dict]:
    """
    Construye contextos de anuncios a partir del input
    """

    ads_data = get_ads_by_scope(gaql, input_row, metrics)

    contexts = []

    for ad in ads_data:
        contexts.append(_build_single_context(ad))

    return contexts


def _build_single_context(ad: dict) -> Dict:
    """
    Construye un único contexto a partir de los datos normalizados del anuncio
    """
    #Extraemos el idioma del nombre de la campaña
    campaign_name = ad.get("campaign_name")

    pais = None
    idioma = None

    try:
        pais, idioma = extract_pais_idioma_from_campaign(campaign_name)
    except Exception:
        # Se deja vacío para que el control gestione el error
        pass

    #Extraemos el destino del nombre de la cuenta
    account_name = ad.get("account_name")

    destino = None

    try:
        destino = extract_destino_from_account(account_name)
    except Exception:
        # Se deja vacío para que el control gestione el error
        pass

    return {
        "customer_id": ad["customer_id"],
        "campaign_id": ad["campaign_id"],
        "ad_group_id": ad["ad_group_id"],
        "ad_id": ad["ad_id"],

        "campaign": {
            "campaign_name": ad["campaign_name"],
            "campaign_type": ad["campaign_type"]
        },

        "ad_group": {
            "ad_group_name": ad["ad_group_name"]
        },

        "ad": {
            "ad_id": ad["ad_id"],
            "type": ad["ad_type"],
            "final_urls": ad["final_urls"],
            "status": ad["ad_status"]
        },

        "business": {
            "pais": pais,
            "idioma": idioma,
            "destino": destino
        },

        "assets": [],
        "headlines": [],
        "descriptions": [],
        "metrics": {}
    }