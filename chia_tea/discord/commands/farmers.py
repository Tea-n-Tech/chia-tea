from typing import List

from chia_tea.discord.formatting import farmer_harvester_pb2_as_markdown

from ..common import catch_errors_as_message, open_database_read_only
from ..formatting import get_machine_info_name
from ..notifications.run_notifiers import get_current_computer_and_machine_infos_from_db


@catch_errors_as_message
async def farmers_cmd(db_filepath: str) -> List[str]:
    """Formats all farmers into a message

    Parameters
    ----------
    db_filepath : str
        path to the sqlite database

    Returns
    -------
    messages : List[str]
        list of messages to print
    """
    messages = []

    with open_database_read_only(db_filepath) as cursor:

        machine_and_computer_info_dict = get_current_computer_and_machine_infos_from_db(cursor)

        messages = []

        for _, (machine, computer_info) in machine_and_computer_info_dict.items():
            farmer_is_running = computer_info.farmer.is_running

            # a farmer is running, create a message
            if farmer_is_running:
                messages += [f"🧑‍🌾 *{get_machine_info_name(machine)}*:"]

                # list up connected harvesters
                messages += [
                    farmer_harvester_pb2_as_markdown(harvester)
                    for harvester in computer_info.farmer_harvesters
                ]

        if not messages:
            messages.append("No farmers 🧑‍🌾 around.")

    return messages
