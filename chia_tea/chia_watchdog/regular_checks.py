
from chia_tea.chia_watchdog.ChiaWatchdog import ChiaWatchdog


# NOT NEEDED ANYMORE BUT LEFT AS EXAMPLE!
# pylint: disable=unused-argument
def check_something(watchdog: ChiaWatchdog):
    """ Check something e.g. possibly modify the harvester

    Parameters
    ----------
    watchdog : ChiaWatchdog
        Watchdog to run regular checks on
    """


async def run_watchdog_checks(watchdog: ChiaWatchdog):
    """ Runs the harvester checks. Checks allow modification.

    Parameters
    ----------
    watchdog : ChiaWatchdog
        Watchdog to run regular checks on
    """

    for check_func in ALL_HARVESTER_CHECKS:
        check_func(watchdog=watchdog)


ALL_HARVESTER_CHECKS = [
    check_something
]
