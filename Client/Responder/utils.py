import logging
from typing import Optional

import time
from logging import Logger


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


class timer:
    """
    util function used to log the time taken by a part of program
    """

    def __init__(self, logger: Logger, message: str):
        """
        init the timer

        Parameters
        ----------
        logger: Logger
            logger to write the logs
        message: str
            message to log, like start xxx
        """
        self.message = message
        self.logger = logger
        self.start = 0
        self.duration = 0
        self.sub_timers = []

    def __enter__(self):
        """
        context enter to start write this
        """
        self.start = time.time()
        self.logger.info("Starting %s" % self.message)
        return self

    def __exit__(self, context, value, traceback):
        """
        context exit will write this
        """
        self.duration = time.time() - self.start
        self.logger.info(f"Finished {self.message}, that took {self.duration:.3f}")
