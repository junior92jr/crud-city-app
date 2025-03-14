import logging


def logger_config(module: str, level=logging.DEBUG) -> logging.Logger:
    """Creates and configures a logger for a given module."""

    logger = logging.getLogger(module)
    if not logger.hasHandlers():
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s] %(message)s"
        )

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        logger.setLevel(level)
        logger.addHandler(handler)

    return logger
