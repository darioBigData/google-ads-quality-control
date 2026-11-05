import os
import logging


def create_logger(logs_dir, run_id, level="INFO"):

    os.makedirs(logs_dir, exist_ok=True)

    log_path = os.path.join(logs_dir, f"log_{run_id}.txt")

    logger = logging.getLogger(run_id)
    logger.setLevel(level)

    fh = logging.FileHandler(log_path)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)

    logger.addHandler(fh)

    return logger


def log_info(logger, msg):
    logger.info(msg)


def log_error(logger, msg):
    logger.error(msg)