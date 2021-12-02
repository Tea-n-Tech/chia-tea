import asyncio
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Callable


def async_test(fun: Callable):
    """Decorator for running async tests

    Parameters
    ----------
    f : function
        async test function to wrap
    """

    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(fun(*args, **kwargs))

    return wrapper


@contextmanager
def set_directory(path: str):
    """Sets the cwd within the context

    Parameters
    ----------
    path : str
        The path to the cwd
    """

    origin = Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)
