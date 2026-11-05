from core.context_utils import extract_destino_from_account_name

def get_customer_data(gaql, customer_id, metrics):

    query = """
    SELECT
        customer.id,
        customer.descriptive_name
    FROM customer
    """

    rows = gaql.query(
        customer_id=customer_id,
        sql=query
    )

    metrics["total_calls"] += 1

    if not rows:
        return {}

    r = rows[0]

    customer_name = r["customer.descriptive_name"]

    destino = extract_destino_from_account_name(customer_name)

    return {
        "customer_id": r["customer.id"],
        "customer_name": r["customer.descriptive_name"],
        "destino": destino
    }
