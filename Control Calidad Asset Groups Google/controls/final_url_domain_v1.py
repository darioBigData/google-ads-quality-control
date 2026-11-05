from urllib.parse import urlparse

from core.context_utils import (
    get_account_destino,
    safe_join_for_output
)


DESTINO_DOMAIN_MAP = {

    "BKV": "blinkvox.com",
    "CIF": "calminform.com",
    "EDU": "edufindly.com",
    "IGN": "ignaly.com",

    "SEK": "seekandyeshallfind.co",
    "DSR": "discoverysearcher.com",
    "BES": "bestentertainmentspot.com",
    "FQQ": "fastqueryquest.com",
    "FAE": "fastanswerexplore.com",
    "MSP": "mindspark.com",
    "IQI": "inquiryinsider.com",
    "ASF": "answersfetcher.com"
}


def extract_domain(url: str):

    if not url:
        return None

    try:

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        if domain.startswith("www."):
            domain = domain[4:]

        return domain

    except Exception:
        return None


def run(context: dict) -> dict:

    control_id = "AG002"

    try:
        asset_group = context.get("asset_group", {})
        final_urls = asset_group.get("final_urls", [])

        destino = get_account_destino(context)

        if not destino:

            return {
                "control_id": control_id,
                "status": "ERROR_TECNICO",
                "valor_esperado": "Destino disponible",
                "valor_encontrado": None,
                "detalle": "No se pudo extraer destino de la cuenta",
                "error_tecnico": "account.destino missing"
            }

        expected_domain = DESTINO_DOMAIN_MAP.get(destino)

        if not expected_domain:

            return {
                "control_id": control_id,
                "status": "ERROR_TECNICO",
                "valor_esperado": "Destino presente en mapping",
                "valor_encontrado": destino,
                "detalle": "Destino no definido en DESTINO_DOMAIN_MAP",
                "error_tecnico": f"destino {destino} not mapped"
            }

        if not final_urls:

            return {
                "control_id": control_id,
                "status": "SKIP",
                "valor_esperado": expected_domain,
                "valor_encontrado": None,
                "detalle": "Asset group sin final URLs",
                "error_tecnico": None
            }

        invalid_urls = []

        for url in final_urls:

            domain = extract_domain(url)

            if not domain or expected_domain not in domain:

                invalid_urls.append(url)

        if invalid_urls:

            return {
                "control_id": control_id,
                "status": "ERROR",
                "valor_esperado": expected_domain,
                "valor_encontrado": safe_join_for_output(invalid_urls),
                "detalle": "Dominio de Final URL no coincide con el destino",
                "error_tecnico": None
            }

        return {
            "control_id": control_id,
            "status": "OK",
            "valor_esperado": expected_domain,
            "valor_encontrado": expected_domain,
            "detalle": None,
            "error_tecnico": None
        }

    except Exception as e:

        return {
            "control_id": control_id,
            "status": "ERROR_TECNICO",
            "valor_esperado": None,
            "valor_encontrado": None,
            "detalle": None,
            "error_tecnico": str(e)
        }