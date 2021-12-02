import datetime
import unittest

from ....models.ChiaWatchdog import ChiaWatchdog
from ....models.MadMaxPlotInProgress import MadMaxPercentages, MadMaxPlotInProgress
from .line_checks import (
    AddNewPlotInProgress,
    LatestPlotEnteringPhase2,
    LatestPlotEnteringPhase3,
    LatestPlotEnteringPhase4,
    SetFarmerPublicKeyForLatestPlot,
    SetLatestPlotProgressForPhase1,
    SetLatestPlotProgressForPhase2,
    SetLatestPlotProgressForPhase3,
    SetPlotDataForLatestPlot,
    SetPoolPublicKeyForLatestPlot,
    StartCopyOfPlot,
)


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

    def test_plot_entering_phase2(self):

        logfile_line = "[P2] max_table_size = 4295062806"

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

        action = LatestPlotEnteringPhase2()
        self.assertTrue(action.is_match(logfile_line))
        action.apply(line=logfile_line, chia_dog=dog)
        self.assertEqual(dog.plots_in_progress, [plot])
        self.assertEqual(plot.state, "Plotting Phase2")

    def test_update_progress_for_phase2(self):

        lines = [
            "[P2] Table 7 scan took 39.6447 sec",
            "[P2] Table 7 rewrite took 134.675 sec, dropped 0 entries (0 %)",
            "[P2] Table 6 scan took 49.1251 sec",
            "[P2] Table 6 rewrite took 120.439 sec, dropped 581252134 entries (13.5333 %)",
            "[P2] Table 5 scan took 47.7513 sec",
            "[P2] Table 5 rewrite took 108.784 sec, dropped 761979853 entries (17.7412 %)",
            "[P2] Table 4 scan took 44.9049 sec",
            "[P2] Table 4 rewrite took 105.015 sec, dropped 828797543 entries (19.2969 %)",
            "[P2] Table 3 scan took 48.4281 sec",
            "[P2] Table 3 rewrite took 111.87 sec, dropped 855125503 entries (19.9095 %)",
            "[P2] Table 2 scan took 44.8467 sec",
            "[P2] Table 2 rewrite took 106.716 sec, dropped 865599957 entries (20.1538 %)",
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

        action = SetLatestPlotProgressForPhase2()
        for i_line, line in enumerate(lines):
            self.assertTrue(action.is_match(line))
            action.apply(line=line, chia_dog=dog)
            self.assertEqual(dog.plots_in_progress, [plot])
            self.assertEqual(plot.progress, MadMaxPercentages.phase2[i_line])

    def test_plot_entering_phase3(self):

        logfile_line = "Wrote plot header with 268 bytes"

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

        action = LatestPlotEnteringPhase3()
        self.assertTrue(action.is_match(logfile_line))
        action.apply(line=logfile_line, chia_dog=dog)
        self.assertEqual(dog.plots_in_progress, [plot])
        self.assertEqual(plot.state, "Plotting Phase3")

    def test_update_progress_for_phase3(self):

        lines = [
            "[P3-1] Table 2 took 119.469 sec, wrote 3429382107 right entries",
            "[P3-2] Table 2 took 114.577 sec, wrote 3429382107 left entries, 3429382107 final",
            "[P3-1] Table 3 took 143.732 sec, wrote 3439937303 right entries",
            "[P3-2] Table 3 took 131.013 sec, wrote 3439937303 left entries, 3439937303 final",
            "[P3-1] Table 4 took 132.11 sec, wrote 3466170141 right entries",
            "[P3-2] Table 4 took 158.274 sec, wrote 3466170141 left entries, 3466170141 final",
            "[P3-1] Table 5 took 133.552 sec, wrote 3532993351 right entries",
            "[P3-2] Table 5 took 140.348 sec, wrote 3532993351 left entries, 3532993351 final",
            "[P3-1] Table 6 took 141.1 sec, wrote 3713716370 right entries",
            "[P3-2] Table 6 took 145.006 sec, wrote 3713716370 left entries, 3713716370 final",
            "[P3-1] Table 7 took 177.476 sec, wrote 4294916656 right entries",
            "[P3-2] Table 7 took 162.498 sec, wrote 4294916656 left entries, 4294916656 final",
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

        action = SetLatestPlotProgressForPhase3()
        for i_line, line in enumerate(lines):
            self.assertTrue(action.is_match(line))
            action.apply(line=line, chia_dog=dog)
            self.assertEqual(dog.plots_in_progress, [plot])
            self.assertEqual(plot.progress, MadMaxPercentages.phase3[i_line])

    def test_plot_entering_phase4(self):

        logfile_line = "[P4] Starting to write C1 and C3 tables"

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

        action = LatestPlotEnteringPhase4()
        self.assertTrue(action.is_match(logfile_line))
        action.apply(line=logfile_line, chia_dog=dog)
        self.assertEqual(dog.plots_in_progress, [plot])
        self.assertEqual(plot.state, "Plotting Phase4")
