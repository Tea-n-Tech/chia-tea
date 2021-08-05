import asyncio
from typing import Callable


def async_test(fun: Callable):
    """ Decorator for running async tests

    Parameters
    ----------
    f : function
        async test function to wrap
    """

    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(fun(*args, **kwargs))
    return wrapper
