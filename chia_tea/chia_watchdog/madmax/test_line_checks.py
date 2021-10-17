import datetime
import unittest

from chia_tea.chia_watchdog.madmax.MadMaxPlotInProgress import MadMaxPlotInProgress
from .line_checks import StartCopyOfPlot
from ..ChiaWatchdog import ChiaWatchdog


class TestLineAction(unittest.TestCase):
    def test_plotting_plot_is_removed_after_finish(self):

        public_key = "72fff9b4f41767c333314a126c06242297c3f20f44bcf1da1a82c7ec7eb8afaf"
        logfile_line = f"Started copy to /some/drive/plot-k32-2021-10-06-00-53-{public_key}.plot"

        dog = ChiaWatchdog("", "")
        dog.plots_in_progress.append(
            MadMaxPlotInProgress(
                process_id=1,
                public_key=public_key,
                farmer_public_key="",
                pool_public_key="",
                start_time=datetime.datetime.now(),
                progress=0.0,
                plot_type=32,
                state="",
            )
        )

        action = StartCopyOfPlot()
        self.assertTrue(action.is_match(logfile_line))
        action.apply(line=logfile_line, chia_dog=dog)
        self.assertEqual(dog.plots_in_progress, [])
