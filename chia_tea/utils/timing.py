

import asyncio
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Union

MILLISECOND = 1e-3
MICROSECONDS = 1e-6
SECOND = 1
MINUTE = 60
HOUR = 60 * 60
DAY = 24 * 60 * 60


def format_timedelta_from_secs(seconds: Union[float, None]) -> str:
    """Format datetime into a better format

    Parameters
    ----------
    seconds : Union[float, None]
        timedelta in seconds

    Returns
    -------
    response: str
        nicely formatted timedelta
    """

    if seconds is None:
        return ""

    response_short = "{0:.0f}{1}"
    response_long = "{0:.2f}{1}"

    if seconds < MILLISECOND:
        return response_short.format(seconds / MICROSECONDS, "µs")

    if seconds < SECOND:
        return response_short.format(seconds / MILLISECOND, "ms")

    if seconds < MINUTE:
        return response_long.format(seconds / SECOND, "s")

    if seconds < HOUR:
        return response_long.format(seconds / MINUTE, "m")

    # if seconds < DAY:
    return response_long.format(seconds / HOUR, "h")


def format_timedelta(delta_time: Union[timedelta, None]) -> str:
    """Format datetime into a better format

    Parameters
    ----------
    delta_time: Union[timedelta, None]
        timedelta object to format

    Returns
    -------
    response: str
        datetime object nicely formatted
    """

    if delta_time is None:
        return ""

    dt_secs = delta_time.total_seconds()

    return format_timedelta_from_secs(dt_secs)


async def async_throttle(min_duration: float):
    """ Logs the time of the function call

    Parameters
    ----------
    min_duration : float
        minimum duration the function will take
    """
    def decorator(function):
        @wraps(function)
        async def _throttle_it(*args, **kwargs):
            start_time = datetime.now()
            try:
                return await function(*args, **kwargs)
            finally:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                wait_duration = max(0, min_duration - duration)
                await asyncio.sleep(wait_duration)
        return _throttle_it
    return decorator


async def wait_at_least(
        min_duration: float,
        start_time: Optional[datetime] = None):
    """ This function delays until at least the duration has
    passed since the specified start time

    Parameters
    ----------
    min_duration : float
        minimum duration to wait since the start time
    start_time : Optional[datetime]
        optional starting time. Will be set as now if not specified.
    """

    start_time = datetime.now() if start_time is None else start_time
    duration = (datetime.now() - start_time).total_seconds()

    await asyncio.sleep(max(0, min_duration - duration))
