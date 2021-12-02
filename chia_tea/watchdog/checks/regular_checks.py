from typing import Dict
import psutil

from ...models.ChiaWatchdog import ChiaWatchdog


# pylint: disable=unused-argument
def remove_plotting_plots_if_madmax_does_not_run(watchdog: ChiaWatchdog):
    """Removes the plotting plots if the plotting process was killed

    Parameters
    ----------
    watchdog : ChiaWatchdog
        Watchdog to run regular checks on
    """
    process_ids = [plot.process_id for plot in watchdog.plots_in_progress if plot.process_id > 0]

    process_cache: Dict[int, psutil.Process] = {}
    dead_process_ids = []
    for pid in process_ids:
        try:
            process = process_cache.get(pid) or psutil.Process(pid)
            process_cache[process.pid] = process
            if process.is_running() and "chia_plot" in process.exe():
                # all good
                pass
            else:
                dead_process_ids.append(pid)
        except psutil.NoSuchProcess:
            dead_process_ids.append(pid)

    watchdog.plots_in_progress = [
        plot for plot in watchdog.plots_in_progress if plot.process_id not in dead_process_ids
    ]


async def run_watchdog_checks(watchdog: ChiaWatchdog):
    """Runs the harvester checks. Checks allow modification.
    Parameters
    ----------
    watchdog : ChiaWatchdog
        Watchdog to run regular checks on
    """

    for check_func in ALL_HARVESTER_CHECKS:
        check_func(watchdog=watchdog)


ALL_HARVESTER_CHECKS = [remove_plotting_plots_if_madmax_does_not_run]
