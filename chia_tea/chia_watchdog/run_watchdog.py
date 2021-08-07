
import asyncio
import traceback

from ..utils.logger import get_logger
from .api.update_all import update_directly_from_chia
from .ChiaWatchdog import ChiaWatchdog
from .logfile.file_watching import watch_lines_infinitely
from .logfile.line_checks import run_line_checks
from .regular_checks import run_watchdog_checks


async def __start_watchdog_self_checks(chia_dog: ChiaWatchdog):
    """ Endless checking of the wathcdog such as timeouts
    """
    await chia_dog.ready()

    while True:
        await run_watchdog_checks(chia_dog)
        await asyncio.sleep(0.8)


def __get_on_ready_function(chia_dog: ChiaWatchdog):
    """ Returns a function setting the watchog to be ready
    """
    async def __on_ready():
        chia_dog.set_as_ready()
    return __on_ready


async def __start_updating_watchdog_service_infos(chia_dog: ChiaWatchdog):
    """ Infinite loop to update the service info data of the watchdog regularly
    """
    while True:
        # contact chia on same machine and update tracking data
        await update_directly_from_chia(chia_dog=chia_dog)

        # the timeout is around 4s so faster does not make sense
        await asyncio.sleep(7)


def __get_function_to_update_chia_dog_on_line(chia_dog: ChiaWatchdog):
    """ Wrapper function to bring chia_dog into the context of
    the line updating function
    """

    async def _on_line_function(line: str):
        await run_line_checks(chia_dog, line)

    return _on_line_function


async def run_watchdog(
    chia_dog: ChiaWatchdog,
):
    """ Start observing chia

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
                # infinite watching of the logfile
                watch_lines_infinitely(
                    chia_dog.logfile_filepath,
                    on_ready=__get_on_ready_function(chia_dog),
                    on_line=__get_function_to_update_chia_dog_on_line(
                        chia_dog),
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
