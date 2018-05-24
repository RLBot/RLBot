import inspect
import logging


DEFAULT_LOGGER = 'rlbot'
logger_initialized = False
logging_level = logging.INFO
FORMAT = "%(levelname)s:%(name)5s[%(filename)20s:%(lineno)s - %(funcName)20s() ] %(message)s"


def get_logger(logger_name, log_creation=True):
    global logger_initialized
    if not logger_initialized:
        logging.basicConfig(format=FORMAT, level=logging_level)
        logging.getLogger().setLevel(logging_level)
        logger_initialized = True
    logger = logging.getLogger(logger_name)
    if logger_name == DEFAULT_LOGGER:
        return logger
    logger.setLevel(logging_level)
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
