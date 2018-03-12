import inspect
import logging

logger_initialized = False
logging_level = logging.DEBUG
FORMAT = "%(levelname)s:%(name)5s[%(filename)20s:%(lineno)s - %(funcName)20s() ] %(message)s"


def get_logger(logger_name):
    global logger_initialized
    if not logger_initialized:
        logging.basicConfig(format=FORMAT, level=logging_level)
        logging.getLogger().setLevel(logging_level)
        logger_initialized = True
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_level)

    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    parent_call = calframe[1]
    file_name = parent_call.filename
    logger.debug('creating logger for %s', file_name)
    return logger
