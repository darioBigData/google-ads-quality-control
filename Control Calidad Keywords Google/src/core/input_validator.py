import os


def validate_input_file(input_path, separator=";"):

    # =========================
    # EXISTENCIA
    # =========================
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"El fichero de input no existe: {input_path}")

    rows = []

    with open(input_path, "r", encoding="utf-8") as f:

        lines = f.readlines()

        if not lines:
            raise ValueError("El fichero de input está vacío")

        # =========================
        # CABECERA
        # =========================
        headers = lines[0].strip().split(separator)

        required_fields = ["customer_id"]

        for field in required_fields:
            if field not in headers:
                raise ValueError(f"Falta campo obligatorio en input: {field}")

        # =========================
        # FILAS
        # =========================
        for i, line in enumerate(lines[1:], start=2):

            if not line.strip():
                continue  # ignorar líneas vacías

            values = line.strip().split(separator)

            if len(values) != len(headers):
                raise ValueError(
                    f"Fila {i} mal formada: nº columnas incorrecto"
                )

            row = dict(zip(headers, values))

            # =========================
            # VALIDACIONES
            # =========================
            if not row.get("customer_id"):
                raise ValueError(f"Fila {i}: customer_id es obligatorio")

            rows.append(row)

    if not rows:
        raise ValueError("No hay filas válidas en el input")

    return rows