import logging
from typing import Optional


def get_logger(logger_name: Optional[str] = None, stream: bool = True):
    """
    init the logger, give it proper format, log them both in terminal stream and file
    """
    logging.basicConfig(
        format="%(name)s: %(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d:%H:%M:%S",
        level=logging.INFO,
    )

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    formatter = logging.Formatter(
        "CLIENT: %(name)s | %(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    )
    if not logger.hasHandlers() and stream:
        stdout_handler = logging.StreamHandler()
        stdout_handler.setFormatter(formatter)
        stdout_handler.setLevel(logging.INFO)
        logger.addHandler(stdout_handler)

    return logger
