
import inspect
import logging
import os
import sys
import traceback
from functools import wraps
from logging import StreamHandler
from time import time
from typing import Callable

from concurrent_log_handler import ConcurrentRotatingFileHandler

from ..protobuf.generated.config_pb2 import DEBUG, ERROR, INFO, TRACE, WARNING
from .config import get_config

TRACE_LEVEL = 5
TRACE_NAME = "TRACE"
logging.addLevelName(TRACE_LEVEL, TRACE_NAME)


def __parse_loglevel(level: str) -> int:
    """ Parse the log leve froms string into integer

    Parameters
    ----------
    level : str
        one of: DEBUG, INFO, WARNING, ERROR

    Returns
    -------
    loglevel : int
        log leve as int for the logging module
    """
    if level == INFO:
        return logging.INFO
    if level == DEBUG:
        return logging.DEBUG
    if level == WARNING:
        return logging.WARNING
    if level == ERROR:
        return logging.ERROR
    if level == TRACE:
        return TRACE_LEVEL

    msg = (
        f"Name '{0}' is not an a correct log level."
        "Try one of TRACE, DEBUG, INFO, WARNING, ERROR.")
    raise ValueError(msg.format(level))


def __add_handler_only_once(
    logger: logging.Logger,
    handler: logging.Handler,
    handler_type: type
):
    """ Adds a handler only if there is none of the same class yet

    Parameters
    ----------
    logger : logging.Logger
        logger to add handler to
    handler : logging.Handler
        handler to add
    """
    if not any(isinstance(handler, handler_type)
               for handler in logger.handlers):
        logger.addHandler(handler)


def get_logger(
    name: str,
) -> logging.Logger:
    """ Get a logger with a (module) name

    Parameters
    ----------
    name : str
        name of the logger, preferably '__name__' for modules

    Returns
    -------
    logger : logging.Logger
    """
    new_logger = logging.getLogger(name)
    config = get_config().logging

    # print to stdout
    #
    # must be BEFORE file handler otherwise it will
    # not be added due to the logger type check
    if config.log_to_console:
        __add_handler_only_once(
            new_logger,
            StreamHandler(stream=sys.stdout),
            StreamHandler,
        )

    # log to file if possible
    try:
        # setup log handler (file)
        directory: str = os.path.join(
            os.path.expanduser("~/.chia_tea/log"),
        )
        os.makedirs(directory, exist_ok=True)

        if config.log_to_file:
            handler = ConcurrentRotatingFileHandler(
                os.path.join(directory, "chia_tea.log"),
                maxBytes=config.max_logfile_size_mb * 1024 * 1024,
                backupCount=config.max_logfiles,
            )
            formatter = logging.Formatter(
                fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            handler.setFormatter(formatter)
            __add_handler_only_once(
                new_logger,
                handler,
                ConcurrentRotatingFileHandler
            )

    # pylint: disable=broad-except
    except Exception:
        err_msg = traceback.format_exc()
        logging.getLogger(__name__).error(err_msg)

    # loglevel
    loglevel_str = config.loglevel
    loglevel = __parse_loglevel(loglevel_str)
    new_logger.setLevel(loglevel)

    return new_logger


def get_function_name(function: Callable) -> str:
    """ Get the proper name of a function as string

    Parameters
    ----------
    function : Callable
        function to get the name from

    Returns
    -------
    name : str
    """
    name = function.__module__ + "." + function.__name__

    for cls in inspect.getmro(function.__class__):
        if function.__name__ in cls.__dict__:
            name += cls.__name__ + name

    return name


def log_runtime_async(module_name: str):
    """ Logs the time of the function call

    Parameters
    ----------
    func : Callable
    """
    def decorator(function):
        @wraps(function)
        async def _time_it(*args, **kwargs):
            start = time()
            try:
                return await function(*args, **kwargs)
            finally:
                get_logger(module_name).log(
                    TRACE_LEVEL,
                    "{0} took {1:.2f}s".format(
                        get_function_name(function),
                        time() - start,
                    )
                )
        return _time_it
    return decorator
