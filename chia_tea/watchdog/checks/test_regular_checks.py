import unittest
from datetime import datetime
from unittest import mock

import psutil

from ...models.ChiaWatchdog import ChiaWatchdog
from ...models.MadMaxPlotInProgress import MadMaxPlotInProgress
from .regular_checks import remove_plotting_plots_if_madmax_does_not_run


class TestRegularChecks(unittest.TestCase):
    def test_plotting_plot_is_not_removed_if_plotting_job_is_running(self):

        watchdog = ChiaWatchdog("", "")
        watchdog.plots_in_progress = [
            MadMaxPlotInProgress(
                process_id=1,
                farmer_public_key="",
                pool_public_key="",
                public_key="",
                start_time=datetime.now(),
                progress=0,
                plot_type=32,
                state="",
            )
        ]
        with mock.patch("psutil.Process", mock.MagicMock()) as MockedProcess:
            MockedProcess = MockedProcess.return_value
            MockedProcess.is_running.return_value = True
            MockedProcess.exe.return_value = "chia_plot"
            remove_plotting_plots_if_madmax_does_not_run(watchdog)
        self.assertEqual(len(watchdog.plots_in_progress), 1)

    def test_plotting_plot_is_removed_if_plotting_job_is_gone(self):

        watchdog = ChiaWatchdog("", "")
        plot = MadMaxPlotInProgress(
            process_id=1,
            farmer_public_key="",
            pool_public_key="",
            public_key="",
            start_time=datetime.now(),
            progress=0,
            plot_type=32,
            state="",
        )
        watchdog.plots_in_progress = [plot]
        with mock.patch("psutil.Process", mock.MagicMock()) as MockedProcess:
            MockedProcess.side_effect = psutil.NoSuchProcess(100, "", "")
            remove_plotting_plots_if_madmax_does_not_run(watchdog)
        self.assertEqual(len(watchdog.plots_in_progress), 0)

        watchdog.plots_in_progress = [plot]
        with mock.patch("psutil.Process", mock.MagicMock()) as MockedProcess:
            MockedProcess = MockedProcess.return_value
            MockedProcess.is_running.return_value = True
            MockedProcess.exe.return_value = "some_other_program"
            remove_plotting_plots_if_madmax_does_not_run(watchdog)
        self.assertEqual(len(watchdog.plots_in_progress), 0)

        watchdog.plots_in_progress = [plot]
        with mock.patch("psutil.Process", mock.MagicMock()) as MockedProcess:
            MockedProcess.is_running.return_value = False
            MockedProcess.exe.return_value = "pewpew/chia_plot"
            remove_plotting_plots_if_madmax_does_not_run(watchdog)
        self.assertEqual(len(watchdog.plots_in_progress), 0)
