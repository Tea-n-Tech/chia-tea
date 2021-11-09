from typing import List

from ..common import catch_errors_as_message, open_database_read_only
from ..formatting import get_machine_info_name, plot_in_progress_pb2_as_markdown
from ..notifications.run_notifiers import get_current_computer_and_machine_infos_from_db


@catch_errors_as_message
async def plotters_cmd(db_filepath: str) -> List[str]:
    """Formats all harvesters into a message

    Parameters
    ----------
    db_filepath : str
        path to the sqlite database

    Returns
    -------
    messages : List[str]
        list of messages to print
    """
    messages: List[str] = []

    with open_database_read_only(db_filepath) as cursor:

        machine_and_computer_info_dict = get_current_computer_and_machine_infos_from_db(cursor)

        for _, (machine, computer_info) in machine_and_computer_info_dict.items():
            if computer_info.plotting_plots:
                messages.append(
                    "\n".join(
                        (f"  🛠️ Plotter {get_machine_info_name(machine)}",)
                        + tuple(
                            plot_in_progress_pb2_as_markdown(plot)
                            for plot in computer_info.plotting_plots
                        )
                    )
                )

        if not messages:
            messages.append("No Plotters 🛠️ at work.")

    return messages
