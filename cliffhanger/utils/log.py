"""Logging packages."""
import logging
import os

def initialize_logging(log_filename):
    """Initialize logging to file.

    Args:
        log_filename (str): the filename to log to
    """
    try:
        os.makedirs(os.path.dirname(log_filename))
    except FileExistsError:
        pass
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s',
                        handlers=[logging.FileHandler(log_filename, mode='a'),
                                  stream_handler])
    logger = logging.getLogger('sqlitedict')
    logger.propagate = False


initialize_logging("logs/app_logs.log")
