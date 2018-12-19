import inspect
import logging


DEFAULT_LOGGER = 'rlbot'
logging_level = logging.INFO
FORMAT = "%(levelname)s:%(name)5s[%(filename)20s:%(lineno)s - %(funcName)20s() ] %(message)s"

logging.getLogger().setLevel(logging.NOTSET)


def get_logger(logger_name, log_creation=True):
    logger = logging.getLogger(logger_name)
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(FORMAT))
        ch.setLevel(logging_level)
        logger.addHandler(ch)
    if logger_name == DEFAULT_LOGGER:
        return logger
    if log_creation:
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        parent_call = calframe[1]
        file_name = parent_call.filename
        logger.debug('creating logger for %s', file_name)
    return logger


def log_warn(message, args):
    """Logs a warning message using the default logger."""
    get_logger(DEFAULT_LOGGER, log_creation=False).log(logging.WARNING, message, *args)


def log(message):
    get_logger(DEFAULT_LOGGER, log_creation=False).log(logging.INFO, message)
