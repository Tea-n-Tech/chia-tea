import os
import traceback
from datetime import datetime
from typing import Tuple

from ...utils.logger import get_logger
from ..ChiaWatchdog import ChiaWatchdog
from ..logfile.line_checks import AbstractLineAction
from .MadMaxPlotInProgress import MadMaxPlotInProgress


class AddNewPlotInProgress(AbstractLineAction):
    LINE_START = "Crafting plot "

    def is_match(self, line: str) -> bool:
        return line.startswith(self.LINE_START)

    def apply(self, line: str, chia_dog: ChiaWatchdog):
        plot_in_progress = MadMaxPlotInProgress(
            start_time=datetime.now(),
            end_time=None,
            pool_public_key="",
            farmer_public_key="",
            public_key="",
            progress=0,
            end_time_copy=None,
            plot_type=0,
            state="initialization",
        )
        chia_dog.plots_in_progress.append(plot_in_progress)


class SetPoolPublicKeyForLatestPlot(AbstractLineAction):
    LINE_START = "Pool Public Key:"

    def is_match(self, line: str) -> bool:
        return line.startswith(self.LINE_START)

    def apply(self, line: str, chia_dog: ChiaWatchdog):
        line = line[len(self.LINE_START) :].strip()

        if chia_dog.plots_in_progress:
            latest_plot = chia_dog.plots_in_progress[-1]
            latest_plot.pool_public_key = line


class SetFarmerPublicKeyForLatestPlot(AbstractLineAction):
    LINE_START = "Farmer Public Key:"

    def is_match(self, line: str) -> bool:
        return line.startswith(self.LINE_START)

    def apply(self, line: str, chia_dog: ChiaWatchdog):
        line = line[len(self.LINE_START) :].strip()

        if chia_dog.plots_in_progress:
            latest_plot = chia_dog.plots_in_progress[-1]
            latest_plot.farmer_public_key = line


class SetPlotDataForLatestPlot(AbstractLineAction):
    LINE_START = "Plot Name:"

    def is_match(self, line: str) -> bool:
        return line.startswith(self.LINE_START)

    def apply(self, line: str, chia_dog: ChiaWatchdog):
        line = line[len(self.LINE_START) :].strip()

        if chia_dog.plots_in_progress:
            plot_name_split = line.split("-")

            _, plot_type, year, month, day, hour, minute, public_key = plot_name_split

            latest_plot = chia_dog.plots_in_progress[-1]
            latest_plot.public_key = public_key
            latest_plot.start_time = datetime(
                int(year), int(month), int(day), int(hour), int(minute)
            )
            # remove the k before e.g. k32
            latest_plot.plot_type = int(plot_type[1:])
            latest_plot.state = "Plotting Phase1"


class SetLatestPlotAsFinished(AbstractLineAction):
    LINE_START = "Total plot creation time was"

    def is_match(self, line: str) -> bool:
        return line.startswith(self.LINE_START)

    def apply(self, line: str, chia_dog: ChiaWatchdog):
        if chia_dog.plots_in_progress:
            latest_plot = chia_dog.plots_in_progress[-1]
            latest_plot.end_time = datetime.now()
            latest_plot.state = "Plotting Done"


class LatestPlotEnteringPhase2(AbstractLineAction):
    LINE_START = "[P2] max_table_size"

    def is_match(self, line: str) -> bool:
        return line.startswith(self.LINE_START)

    def apply(self, line: str, chia_dog: ChiaWatchdog):
        if chia_dog.plots_in_progress:
            latest_plot = chia_dog.plots_in_progress[-1]
            latest_plot.state = "Plotting Phase2"


class LatestPlotEnteringPhase3(AbstractLineAction):
    LINE_START = "Wrote plot header with"

    def is_match(self, line: str) -> bool:
        return line.startswith(self.LINE_START)

    def apply(self, line: str, chia_dog: ChiaWatchdog):
        if chia_dog.plots_in_progress:
            latest_plot = chia_dog.plots_in_progress[-1]
            latest_plot.state = "Plotting Phase3"


class LatestPlotEnteringPhase4(AbstractLineAction):
    LINE_START = "[P4] Starting to write"

    def is_match(self, line: str) -> bool:
        return line.startswith(self.LINE_START)

    def apply(self, line: str, chia_dog: ChiaWatchdog):
        if chia_dog.plots_in_progress:
            latest_plot = chia_dog.plots_in_progress[-1]
            latest_plot.state = "Plotting Phase4"


class StartCopyOfPlot(AbstractLineAction):
    LINE_START = "Started copy to"

    def is_match(self, line: str) -> bool:
        return line.startswith(self.LINE_START)

    def apply(self, line: str, chia_dog: ChiaWatchdog):
        line_split = line.split()
        plot_filepath = line_split[3]
        plot_name = os.path.basename(plot_filepath)
        public_key = plot_name.split("-")[7]

        for plot in chia_dog.plots_in_progress:
            if plot.public_key == public_key:
                plot.state = "Copying"
                break


class FinishedCopyOfPlot(AbstractLineAction):
    LINE_START = "Copy to"

    def is_match(self, line: str) -> bool:
        return line.startswith(self.LINE_START)

    def apply(self, line: str, chia_dog: ChiaWatchdog):
        line_split = line.split()
        plot_filepath = line_split[2]
        plot_name = os.path.basename(plot_filepath)
        public_key = plot_name.split("-")[7]

        for plot in chia_dog.plots_in_progress:
            if plot.public_key == public_key:
                plot.end_time_copy = datetime.now()
                break


async def run_line_checks(chia_dog: ChiaWatchdog, line: str):
    """Processes a line from the logfile

    Parameters
    ----------
    line : str
        logfile line
    """
    try:
        if line:
            for action in ALL_LINE_ACTIONS:
                if action.is_match(line):
                    action.apply(line, chia_dog)

    except Exception:
        trace = traceback.format_exc()
        err_msg = "Error in line: %s\n%s"
        get_logger(__name__).error(err_msg, line, trace)


ALL_LINE_ACTIONS: Tuple[AbstractLineAction, ...] = (
    AddNewPlotInProgress(),
    SetPoolPublicKeyForLatestPlot(),
    SetFarmerPublicKeyForLatestPlot(),
    SetPlotDataForLatestPlot(),
    SetLatestPlotAsFinished(),
    FinishedCopyOfPlot(),
    LatestPlotEnteringPhase2(),
    LatestPlotEnteringPhase3(),
    LatestPlotEnteringPhase4(),
    StartCopyOfPlot(),
)
