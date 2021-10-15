from datetime import datetime

from .ChiaWatchdog import ChiaWatchdog
from ..utils.config import get_config


def remove_finished_plots(watchdog: ChiaWatchdog):
    """Remove plots after they finished plotting

    Parameters
    ----------
    watchdog : ChiaWatchdog
        Watchdog to run regular checks on

    Notes
    -----
        The plots are removed after they finished.
        The duration is twice the send duration to
        the server to make sure the final data
        including the end time were sent to the server.
    """
    config = get_config()
    send_duration = config.monitoring.client.send_update_every.plotting_plot

    plots_to_remove = []
    for i_plot, plot in enumerate(watchdog.plots_in_progress):
        end_time = plot.end_time
        if end_time is not None:
            now = datetime.now()
            duration = now - end_time
            if duration.total_seconds() > send_duration * 2:
                plots_to_remove.append(i_plot)

    for i_plot in reversed(plots_to_remove):
        watchdog.plots_in_progress.pop(i_plot)


async def run_watchdog_checks(watchdog: ChiaWatchdog):
    """Runs the harvester checks. Checks allow modification.

    Parameters
    ----------
    watchdog : ChiaWatchdog
        Watchdog to run regular checks on
    """

    for check_func in ALL_HARVESTER_CHECKS:
        check_func(watchdog=watchdog)


ALL_HARVESTER_CHECKS = [remove_finished_plots]
