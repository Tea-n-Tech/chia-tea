import datetime
import unittest

from chia_tea.chia_watchdog.madmax.MadMaxPlotInProgress import (
    MadMaxPercentages,
    MadMaxPlotInProgress,
)
from .line_checks import (
    AddNewPlotInProgress,
    SetFarmerPublicKeyForLatestPlot,
    SetLatestPlotProgressForPhase1,
    SetPlotDataForLatestPlot,
    SetPoolPublicKeyForLatestPlot,
    StartCopyOfPlot,
)
from ..ChiaWatchdog import ChiaWatchdog


class TestLineAction(unittest.TestCase):
    def setUp(self) -> None:
        self.public_key = "72fff9b4f41767c333314a126c06242297c3f20f44bcf1da1a82c7ec7eb8afaf"

    def test_adding_a_new_plot(self):

        logfile_line = "Process ID: 1374"

        dog = ChiaWatchdog("", "")

        action = AddNewPlotInProgress()
        self.assertTrue(action.is_match(logfile_line))
        some_time = datetime.datetime.now()
        action.apply(line=logfile_line, chia_dog=dog)
        self.assertEqual(len(dog.plots_in_progress), 1)
        plot = dog.plots_in_progress[0]
        self.assertEqual(plot.process_id, 1374)
        self.assertEqual(plot.state, "Init")
        self.assertTrue(plot.start_time > some_time)

    def test_plotting_plot_is_removed_after_finish(self):

        logfile_line = (
            f"Started copy to /some/drive/plot-k32-2021-10-06-00-53-{self.public_key}.plot"
        )

        dog = ChiaWatchdog("", "")
        dog.plots_in_progress.append(
            MadMaxPlotInProgress(
                process_id=1,
                public_key=self.public_key,
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

    def test_pool_public_key_is_set_correctly(self):

        logfile_line = f"Pool Public Key:   {self.public_key}"

        dog = ChiaWatchdog("", "")
        plot = MadMaxPlotInProgress(
            process_id=1,
            public_key=self.public_key,
            farmer_public_key="",
            pool_public_key="",
            start_time=datetime.datetime.now(),
            progress=0.0,
            plot_type=32,
            state="",
        )
        dog.plots_in_progress.append(plot)

        action = SetPoolPublicKeyForLatestPlot()
        self.assertTrue(action.is_match(logfile_line))
        action.apply(line=logfile_line, chia_dog=dog)
        self.assertEqual(dog.plots_in_progress, [plot])
        self.assertEqual(plot.pool_public_key, self.public_key)

    def test_farmer_public_key_is_set_correctly(self):

        logfile_line = f"Farmer Public Key: {self.public_key}"

        dog = ChiaWatchdog("", "")
        plot = MadMaxPlotInProgress(
            process_id=1,
            public_key=self.public_key,
            farmer_public_key="",
            pool_public_key="",
            start_time=datetime.datetime.now(),
            progress=0.0,
            plot_type=32,
            state="",
        )
        dog.plots_in_progress.append(plot)

        action = SetFarmerPublicKeyForLatestPlot()
        self.assertTrue(action.is_match(logfile_line))
        action.apply(line=logfile_line, chia_dog=dog)
        self.assertEqual(dog.plots_in_progress, [plot])
        self.assertEqual(plot.farmer_public_key, self.public_key)

    def test_plot_data_is_set_correctly_for_latest_plot(self):

        logfile_line = f"Plot Name: plot-k32-2021-10-05-20-38-{self.public_key}"

        dog = ChiaWatchdog("", "")
        plot = MadMaxPlotInProgress(
            process_id=1,
            public_key=self.public_key,
            farmer_public_key="",
            pool_public_key="",
            start_time=datetime.datetime.now(),
            progress=0.0,
            plot_type=0,
            state="",
        )
        dog.plots_in_progress.append(plot)

        action = SetPlotDataForLatestPlot()
        self.assertTrue(action.is_match(logfile_line))
        action.apply(line=logfile_line, chia_dog=dog)
        self.assertEqual(dog.plots_in_progress, [plot])
        self.assertEqual(plot.public_key, self.public_key)
        self.assertEqual(plot.start_time.year, 2021)
        self.assertEqual(plot.start_time.month, 10)
        self.assertEqual(plot.start_time.day, 5)
        self.assertEqual(plot.start_time.hour, 20)
        self.assertEqual(plot.start_time.minute, 38)
        self.assertEqual(plot.plot_type, 32)
        self.assertEqual(plot.state, "Plotting Phase1")

    def test_update_progress_for_phase1(self):

        lines = [
            "[P1] Table 1 took 56.4157 sec"
            "[P1] Table 2 took 312.581 sec, found 4294982064 matches"
            "[P1] Table 3 took 440.816 sec, found 4295062806 matches"
            "[P1] Table 4 took 443.39 sec, found 4294967684 matches"
            "[P1] Table 5 took 422.741 sec, found 4294973204 matches"
            "[P1] Table 6 took 368.958 sec, found 4294968504 matches"
            "[P1] Table 7 took 248.694 sec, found 4294916656 matches"
        ]

        dog = ChiaWatchdog("", "")
        plot = MadMaxPlotInProgress(
            process_id=1,
            public_key=self.public_key,
            farmer_public_key="",
            pool_public_key="",
            start_time=datetime.datetime.now(),
            progress=0.0,
            plot_type=32,
            state="",
        )
        dog.plots_in_progress.append(plot)

        action = SetLatestPlotProgressForPhase1()
        for i_line, line in enumerate(lines):
            self.assertTrue(action.is_match(line))
            action.apply(line=line, chia_dog=dog)
            self.assertEqual(dog.plots_in_progress, [plot])
            self.assertEqual(plot.progress, MadMaxPercentages.phase1[i_line])
