import csv
import os


def read_input_csv(root_path):

    input_path = os.path.join(
        root_path,
        "input",
        "input.csv"
    )

    if not os.path.exists(input_path):
        raise FileNotFoundError(
            f"Input CSV no encontrado: {input_path}"
        )

    rows = []

    with open(input_path, "r", encoding="utf-8") as f:

        reader = csv.DictReader(
            f,
            delimiter=";"
        )

        for r in reader:

            row = {
                "customer_id": (r.get("customer_id") or "").strip(),
                "campaign_id": (r.get("campaign_id") or "").strip()
            }

            if not row["customer_id"]:
                continue

            rows.append(row)

    return rows