import colorlog
import logging


def initializeLogger() -> logging.Logger:
    """
    Initialize the single logger instance that is used collectively by the
    rest of the Python files in the spotiviz package.

    Returns:
        The logger instance.
    """
    handler = colorlog.StreamHandler()

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )

    handler.setFormatter(formatter)

    logger = colorlog.getLogger('main')
    logger.addHandler(handler)

    logger.setLevel(logging.DEBUG)

    logger.debug('Initialized logger')

    return logger


LOG = initializeLogger()
