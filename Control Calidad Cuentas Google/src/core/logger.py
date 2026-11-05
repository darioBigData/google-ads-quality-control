from datetime import datetime

def log_line(log_file, level, message, customer_id=None):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if customer_id:
        line = f"[{ts}] [{level}] [customer_id={customer_id}] {message}"
    else:
        line = f"[{ts}] [{level}] {message}"

    log_file.write(line + "\n")
    log_file.flush()
