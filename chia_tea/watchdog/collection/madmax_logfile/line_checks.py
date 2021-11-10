import os
import traceback
from datetime import datetime
from typing import Tuple

from ....general.AbstractLineAction import AbstractLineAction
from ....models.ChiaWatchdog import ChiaWatchdog
from ....models.MadMaxPlotInProgress import MadMaxPercentages, MadMaxPlotInProgress
from ....utils.logger import get_logger


class AddNewPlotInProgress(AbstractLineAction):
    """Add a new plot in progress

    Example Line:
    Process ID: 1374

    Note
    ----
        We could add a new plot on the log cmd before
        but we don't have a process id then and if the
        plotting process dies we can't verify this and
        have zombie plots in progress.
    """

    LINE_START = "Process ID:"

    def is_match(self, line: str) -> bool:
        return line.startswith(self.LINE_START)

    def apply(self, line: str, chia_dog: ChiaWatchdog):

        # Formatter conflict with space before :
        line = line[len(self.LINE_START) :].strip()  # noqa: E203
        process_id = int(line)

        chia_dog.plots_in_progress.append(
            MadMaxPlotInProgress(
                process_id=process_id,
                public_key="",
                pool_public_key="",
                farmer_public_key="",
                start_time=datetime.now(),
                progress=0,
                plot_type=0,
                state="Init",
            )
        )


class SetPoolPublicKeyForLatestPlot(AbstractLineAction):
    """Set the public key for the latest plot in progress

    Example Line:
    Pool Public Key:   ...
    """

    LINE_START = "Pool Public Key:"

    def is_match(self, line: str) -> bool:
        return line.startswith(self.LINE_START)

    def apply(self, line: str, chia_dog: ChiaWatchdog):
        # Formatter conflict with space before :
        line = line[len(self.LINE_START) :].strip()  # noqa: E203

        if chia_dog.plots_in_progress:
            latest_plot = chia_dog.plots_in_progress[-1]
            latest_plot.pool_public_key = line


class SetFarmerPublicKeyForLatestPlot(AbstractLineAction):
    """Set the farmer public key for the latest plot

    Example Line:
    Farmer Public Key: ...
    """

    LINE_START = "Farmer Public Key:"

    def is_match(self, line: str) -> bool:
        return line.startswith(self.LINE_START)

    def apply(self, line: str, chia_dog: ChiaWatchdog):
        # Formatter conflict with space before :
        line = line[len(self.LINE_START) :].strip()  # noqa: E203

        if chia_dog.plots_in_progress:
            latest_plot = chia_dog.plots_in_progress[-1]
            latest_plot.farmer_public_key = line


class SetPlotDataForLatestPlot(AbstractLineAction):
    """Extracts plot data from plot name

    Example Line:
    Plot Name: plot-k32-2021-10-05-22-02-{public key}
    """

    LINE_START = "Plot Name:"

    def is_match(self, line: str) -> bool:
        return line.startswith(self.LINE_START)

    def apply(self, line: str, chia_dog: ChiaWatchdog):
        # Formatter conflict with space before :
        line = line[len(self.LINE_START) :].strip()  # noqa: E203

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


class SetLatestPlotProgressForPhase1(AbstractLineAction):
    """Set the progress for updates during phase 1

    Example Lines:
    [P1] Table 1 took 149.086 sec
    [P1] Table 2 took 313.995 sec, found 4294938576 matches
    [P1] Table 3 took 453.323 sec, found 4294895885 matches
    [P1] Table 4 took 435.455 sec, found 4294851544 matches
    [P1] Table 5 took 392.077 sec, found 4294722099 matches
    [P1] Table 6 took 352.225 sec, found 4294381733 matches
    [P1] Table 7 took 260.078 sec, found 4293784356 matches
    """

    LINE_START = "[P1] Table"

    def is_match(self, line: str) -> bool:
        return line.startswith(self.LINE_START)

    def apply(self, line: str, chia_dog: ChiaWatchdog):
        if chia_dog.plots_in_progress:
            line_split = line.split()
            table_index = int(line_split[2]) - 1

            latest_plot = chia_dog.plots_in_progress[-1]
            latest_plot.progress = MadMaxPercentages.phase1[table_index]


class LatestPlotEnteringPhase2(AbstractLineAction):
    """Set the progress for updates during phase 2

    Example Line:
    [P2] max_table_size = 4294967296
    """

    LINE_START = "[P2] max_table_size"

    def is_match(self, line: str) -> bool:
        return line.startswith(self.LINE_START)

    def apply(self, line: str, chia_dog: ChiaWatchdog):
        if chia_dog.plots_in_progress:
            latest_plot = chia_dog.plots_in_progress[-1]
            latest_plot.state = "Plotting Phase2"


class SetLatestPlotProgressForPhase2(AbstractLineAction):
    """Sets the progress for phase 2

    Steps are:
    [P2] Table 7 scan ...
    [P2] Table 7 rewrite ...
    [P2] Table 6 scan ...
    [P2] Table 6 rewrite ...
    [P2] Table 5 scan ...
    [P2] Table 5 rewrite ...
    [P2] Table 4 scan ...
    [P2] Table 4 rewrite ...
    [P2] Table 3 scan ...
    [P2] Table 3 rewrite ...
    [P2] Table 2 scan ...
    [P2] Table 2 rewrite ...
    """

    LINE_START = "[P2] Table"

    def is_match(self, line: str) -> bool:
        return line.startswith(self.LINE_START)

    def apply(self, line: str, chia_dog: ChiaWatchdog):
        if chia_dog.plots_in_progress:
            line_split = line.split()
            table_index = int(line_split[2]) - 1
            one_more = line_split[3] == "rewrite"
            phase2_index = 11 - 2 * table_index + one_more + 1

            latest_plot = chia_dog.plots_in_progress[-1]
            latest_plot.progress = MadMaxPercentages.phase2[phase2_index]


class LatestPlotEnteringPhase3(AbstractLineAction):
    """Update that the latest plot is entering phase 3

    Example Line:
    Wrote plot header with 268 bytes
    """

    LINE_START = "Wrote plot header with"

    def is_match(self, line: str) -> bool:
        return line.startswith(self.LINE_START)

    def apply(self, line: str, chia_dog: ChiaWatchdog):
        if chia_dog.plots_in_progress:
            latest_plot = chia_dog.plots_in_progress[-1]
            latest_plot.state = "Plotting Phase3"


class SetLatestPlotProgressForPhase3(AbstractLineAction):
    """Sets the progress for phase 2

    Steps are:
    [P3-1] Table 2 ...
    [P3-2] Table 2 ...
    [P3-1] Table 3 ...
    [P3-2] Table 3 ...
    [P3-1] Table 4 ...
    [P3-2] Table 4 ...
    [P3-1] Table 5 ...
    [P3-2] Table 5 ...
    [P3-1] Table 6 ...
    [P3-2] Table 6 ...
    [P3-1] Table 7 ...
    [P3-2] Table 7 ...
    """

    def is_match(self, line: str) -> bool:
        return line.startswith("[P3-1]") or line.startswith("[P3-2]")

    def apply(self, line: str, chia_dog: ChiaWatchdog):
        if chia_dog.plots_in_progress:
            line_split = line.split()
            offset = 2
            table_index = int(line_split[2]) - offset
            one_more = line_split[0][4] == "2"
            phase3_index = 2 * table_index + one_more

            latest_plot = chia_dog.plots_in_progress[-1]
            latest_plot.progress = MadMaxPercentages.phase3[phase3_index]


class LatestPlotEnteringPhase4(AbstractLineAction):
    """Set latest plot entering phase 4

    Example Line:
    [P4] Starting to write C1 and C3 tables
    """

    LINE_START = "[P4] Starting to write"

    def is_match(self, line: str) -> bool:
        return line.startswith(self.LINE_START)

    def apply(self, line: str, chia_dog: ChiaWatchdog):
        if chia_dog.plots_in_progress:
            latest_plot = chia_dog.plots_in_progress[-1]
            latest_plot.state = "Plotting Phase4"


class SetLatestPlotAsFinished(AbstractLineAction):
    """Mark the latest plot as finished

    Example Line:
    Total plot creation time was 5129.61 sec (85.4936 min)
    """

    LINE_START = "Total plot creation time was"

    def is_match(self, line: str) -> bool:
        return line.startswith(self.LINE_START)

    def apply(self, line: str, chia_dog: ChiaWatchdog):
        if chia_dog.plots_in_progress:
            latest_plot = chia_dog.plots_in_progress[-1]
            latest_plot.state = "Plotting Done"
            latest_plot.progress = 1


class StartCopyOfPlot(AbstractLineAction):
    """
    Example line:
    Started copy to /some/drive/plot-k32-2021-10-06-00-53-{public_key}.plot
    """

    LINE_START = "Started copy to"

    def is_match(self, line: str) -> bool:
        return line.startswith(self.LINE_START)

    def apply(self, line: str, chia_dog: ChiaWatchdog):
        line_split = line.split()
        # get plot filepath from line
        plot_filepath = line_split[3]
        # isolate the plot name
        plot_name = os.path.basename(plot_filepath)
        # cut out the public key
        public_key_with_file_ending = plot_name.split("-")[7]
        # remove file ending from public key string
        public_key, _ = os.path.splitext(public_key_with_file_ending)

        # remove plot from plotting list
        chia_dog.plots_in_progress = [
            plot for plot in chia_dog.plots_in_progress if plot.public_key != public_key
        ]


# class FinishedCopyOfPlot(AbstractLineAction):
#     LINE_START = "Copy to"

#     def is_match(self, line: str) -> bool:
#         return line.startswith(self.LINE_START)

#     def apply(self, line: str, chia_dog: ChiaWatchdog):
#         line_split = line.split()
#         plot_filepath = line_split[2]
#         plot_name = os.path.basename(plot_filepath)
#         public_key = plot_name.split("-")[7]

#         for plot in chia_dog.plots_in_progress:
#             if plot.public_key == public_key:
#                 plot.end_time_copy = datetime.now()
#                 break


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
    SetLatestPlotProgressForPhase1(),
    LatestPlotEnteringPhase2(),
    SetLatestPlotProgressForPhase2(),
    LatestPlotEnteringPhase3(),
    SetLatestPlotProgressForPhase3(),
    LatestPlotEnteringPhase4(),
    SetLatestPlotAsFinished(),
    StartCopyOfPlot(),
    # FinishedCopyOfPlot(),
)
