import asyncio
import traceback
from typing import Callable

from ..general.file_watching import watch_lines_infinitely
from ..models.ChiaWatchdog import ChiaWatchdog
from ..utils.logger import get_logger
from .checks.regular_checks import run_watchdog_checks
from .collection.api.update_all import update_directly_from_chia
from .collection.logfile.line_checks import run_line_checks
from .collection.madmax_logfile.line_checks import run_line_checks as run_line_checks_madmax


async def __start_watchdog_self_checks(chia_dog: ChiaWatchdog):
    """Endless checking of the watchdog"""
    await chia_dog.ready()

    while True:
        await run_watchdog_checks(chia_dog)
        await asyncio.sleep(0.8)


def __get_on_ready_function(fn: Callable[[], None]):
    """Returns a function setting the watchog to be ready"""

    async def __on_ready():
        fn()

    return __on_ready


async def __start_updating_watchdog_service_infos(chia_dog: ChiaWatchdog):
    """Infinite loop to update the service info data of the watchdog regularly"""
    while True:
        # contact chia on same machine and update tracking data
        await update_directly_from_chia(chia_dog=chia_dog)

        # the timeout is around 4s so faster does not make sense
        await asyncio.sleep(7)


def __get_function_to_update_chia_dog_on_line(chia_dog: ChiaWatchdog):
    """Wrapper function to bring chia_dog into the context of
    the line updating function
    """

    async def _on_line_function(line: str):
        await run_line_checks(chia_dog, line)

    return _on_line_function


def __get_function_to_update_chia_dog_on_madmax_line(chia_dog: ChiaWatchdog):
    """Wrapper function to bring chia_dog into the context of
    the line updating function
    """

    async def _on_line_function(line: str):
        await run_line_checks_madmax(chia_dog, line)

    return _on_line_function


async def run_watchdog(
    chia_dog: ChiaWatchdog,
):
    """Start observing chia

    Parameters
    ----------
    chia_dog : ChiaWatchdog
        the data of this watchdog will be updated regularly

    Notes
    -----
        Runs the following checks:
        - watches the logfile indefinitely
        - runs regular self checks
        - connects to chia services to retrieve information
    """
    while True:
        try:
            await asyncio.gather(
                # infinite watching of the chia logfile
                watch_lines_infinitely(
                    chia_dog.logfile_filepath,
                    # the watchdog is set ready if the logfile is missing
                    # this might just mean that the machine doesn't run
                    # chia.
                    on_file_missing=__get_on_ready_function(chia_dog.set_chia_logfile_is_ready),
                    on_ready=__get_on_ready_function(chia_dog.set_chia_logfile_is_ready),
                    on_line=__get_function_to_update_chia_dog_on_line(chia_dog),
                ),
                # infinite watchig of the madmax logfile
                watch_lines_infinitely(
                    chia_dog.madmax_logfile,
                    # the watchdog is set ready if the logfile is missing
                    # this might just mean that the machine doesn't run
                    # madmax.
                    on_file_missing=__get_on_ready_function(chia_dog.set_madmax_logfile_is_ready),
                    on_ready=__get_on_ready_function(chia_dog.set_madmax_logfile_is_ready),
                    on_line=__get_function_to_update_chia_dog_on_madmax_line(chia_dog),
                ),
                # regular checks such as time out
                __start_watchdog_self_checks(chia_dog),
                # regular status update from chia services
                __start_updating_watchdog_service_infos(chia_dog),
            )

        except Exception:
            err_msg = traceback.format_exc()
            get_logger(__file__).error(err_msg)
            await asyncio.sleep(5)
