"""
This module contains helper functions for project logging.
"""

import os
import sys
import gzip
import logging
import logging.handlers

__author__ = 'Radim Podola'

LOG_DIR = './log'
LOG_FILENAME = 'cevast.log'


def __namer(name):
    return name + ".gz"


def __rotator(source, dest):
    with open(source, "rb") as src:
        with gzip.open(dest, "wb") as trg:
            trg.writelines(src)
    os.remove(source)


def cli_logger() -> logging.Logger:
    return logging.getLogger('CEVAST_CLI')


# TODO setup separate logger to log some info to the console with use of CLI
# or use click-log ???
def setup_cli_logger() -> logging.Logger:
    """
    Setup the CLI project logger 'CEVAST_CLI'.

    Logger has configured a standard console_handler.

    TODO: add support for colours
    """
    # Setup formatter
    formatter = logging.Formatter('%(message)s')
    cli_logger = logging.getLogger('CEVAST_CLI')
    cli_logger.setLevel(logging.INFO)

    # Setup handler writing error-like logs to console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    cli_logger.addHandler(console_handler)
    return cli_logger


# TODO fix problem with mp logging https://medium.com/@rui.jorge.rei/semi-correct-handling-of-log-rotation-in-multiprocess-python-applications-75c56eca6780
def setup_cevast_logger(debug: bool = False, process_id: bool = False) -> logging.Logger:
    """
    Setup the project logger 'CEVAST'.

    Logger has configured 2 handlers:
        - console_handler to write error-like logs to stdout (>= WARNING)
        - file_handler to write logs into rotating file with compression of rotated files

    Each module-level logger must start with 'cevast.' to inherit the setup.

    TODO: add support for config file
    """
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)

    # Setup formatter
    if process_id:
        formatter = logging.Formatter(
            '[%(process)d] %(asctime)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)s - %(funcName)s() ]',
            datefmt='%m/%d/%Y %H:%M:%S',
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)s - %(funcName)s() ]',
            datefmt='%m/%d/%Y %H:%M:%S',
        )

    # Setup handler writing error-like logs to console
    # console_handler = logging.StreamHandler(sys.stdout)
    # console_handler.setLevel(logging.CRITICAL)
    # console_handler.setFormatter(formatter)

    # Setup handler writing logs to a file with compressing of the rotated files
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(LOG_DIR, LOG_FILENAME), maxBytes=200000000, backupCount=50
    )
    file_handler.setFormatter(formatter)
    file_handler.rotator = __rotator
    file_handler.namer = __namer

    # Setup project logger, not root
    logger = logging.getLogger('cevast')
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.addHandler(file_handler)
    # logger.addHandler(console_handler)

    return logger
