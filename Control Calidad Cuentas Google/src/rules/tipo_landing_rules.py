def resolve_tipo_landing(
    socio: str,
    canal: str,
    config_geo: int
) -> str:
    """
    Resuelve el tipo de landing (SEARCH / RSOC / MRSOC)
    a partir de socio, canal y config_geo.
    """

    if socio is None or canal is None or config_geo is None:
        raise ValueError("Faltan datos para resolver tipo_landing")

    socio = socio.upper().strip()
    canal = canal.upper().strip()

    # --- IAC ---
    if socio == "IAC":

        if canal == "SEARCH":
            
            if 0 <= config_geo <= 300:
                return "SEARCH"

            if 400 <= config_geo <= 409:
                return "RSOC"

            if 410 <= config_geo <= 419:
                return "MRSOC"

        if canal == "GDN":

            if 500 <= config_geo <= 504:
                return "RSOC"

            if 505 <= config_geo <= 509:
                return "MRSOC"

        if canal == "PERFORMANCE MAX":

            if 510 <= config_geo <= 514:
                return "RSOC"

            if 515 <= config_geo <= 519:
                return "MRSOC"

        if canal == "DEMGEN":
            return None


    # --- VSM ---
    if socio == "VSM":

        if canal == "SEARCH":
            if config_geo == 999 or 100 <= config_geo <= 199:
                return "SEARCH"

            if config_geo == 4:
                return "MRSOC"

            if config_geo == 20:
                return "RSOC"

        if canal == "GDN":
            if config_geo in (0, 2):
                return "MRSOC"

            if 5 <= config_geo <= 10:
                return "RSOC"

        if canal == "PERFORMANCE MAX":
            if config_geo in (1, 3):
                return "MRSOC"

            if config_geo == 11:
                return "RSOC"
            
        if canal == "DEMGEN":
            return None    

    # --- Caso no mapeado ---
    raise ValueError(
        f"No se pudo resolver tipo_landing | socio={socio} | canal={canal} | config_geo={config_geo}"
    )
