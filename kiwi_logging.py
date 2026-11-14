"""Shared terminal logger; safe to import across Streamlit reruns."""

import logging


logger = logging.getLogger("kiwi")
logger.setLevel(logging.INFO)
logger.propagate = False
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | KIWi | %(levelname)s | %(threadName)s | %(message)s",
        datefmt="%H:%M:%S",
    ))
    logger.addHandler(handler)
