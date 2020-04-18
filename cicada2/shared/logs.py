import logging


LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s -- %(message)s"
DATE_FORMAT = "%m-%d %H:%M"


# NOTE: get log_level/log_file from env var?
def get_logger(name: str = 'logger', log_file: str = None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    sh = logging.StreamHandler()
    logger.addHandler(sh)
    sh.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    logger.debug('Initialized console logger')

    if log_file:
        # NOTE: May need to sync handlers
        fh = logging.FileHandler(log_file)
        fh.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
        logger.addHandler(fh)
        logger.debug(f"Initialized file logger to {log_file}")

    return logger
