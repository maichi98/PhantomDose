from phandose.constants import PATH_LOGGING_CONFIG
import logging.config
import logging


def get_logger(name: str):

    logging.config.fileConfig(PATH_LOGGING_CONFIG)
    logger = logging.getLogger(name)
    return logger