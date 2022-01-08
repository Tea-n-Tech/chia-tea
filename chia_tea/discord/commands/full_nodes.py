from typing import List

from ..common import catch_errors_as_message, open_database_read_only
from ..formatting import full_node_pb2_as_markdown
from ..notifications.run_notifiers import get_current_computer_and_machine_infos_from_db


@catch_errors_as_message
async def full_nodes_cmd(db_filepath: str) -> List[str]:
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
    messages = []

    with open_database_read_only(db_filepath) as cursor:

        machine_and_computer_info_dict = get_current_computer_and_machine_infos_from_db(cursor)

        for _, (machine, computer_info) in machine_and_computer_info_dict.items():
            if computer_info.full_node.is_running:
                messages.append(
                    full_node_pb2_as_markdown(
                        machine,
                        full_node=computer_info.full_node,
                    )
                )

        if not messages:
            messages.append("No Full Nodes 🏡 around.")

    return messages
