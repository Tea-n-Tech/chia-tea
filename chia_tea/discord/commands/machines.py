from datetime import datetime
from typing import List

from ...protobuf.to_sqlite.sql_cmds import (
    get_cpu_for_machine_from_db,
    get_machine_infos_from_db,
    get_ram_for_machine_from_db,
)
from ..common import catch_errors_as_message, open_database_read_only
from ..formatting import cpu_pb2_as_markdown, get_machine_info_name, ram_pb2_as_markdown


@catch_errors_as_message
async def machines_cmd(db_filepath: str) -> List[str]:
    """Formats all machines into a message

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

        # get all machine infos from the database
        machine_infos, _ = get_machine_infos_from_db(cursor)

        # convert the infos into messages
        for machine_info in machine_infos:
            seconds_since_last_contact = (
                datetime.now() - datetime.fromtimestamp(machine_info.time_last_msg)
            ).total_seconds()
            is_connected = seconds_since_last_contact < 60
            icon = "🟢" if is_connected else "🟠"

            cpus, _ = get_cpu_for_machine_from_db(
                cursor,
                machine_info.machine_id,
            )
            cpu_msgs = [cpu_pb2_as_markdown(cpu) for cpu in cpus]

            rams, _ = get_ram_for_machine_from_db(
                cursor,
                machine_info.machine_id,
            )
            ram_msgs = [ram_pb2_as_markdown(ram) for ram in rams]

            machine_name = get_machine_info_name(machine_info)
            headline = (
                "{icon} {machine_name} responded {seconds_since_last_contact:.1f} seconds ago"
            )
            messages.append(
                "\n".join(
                    [
                        headline.format(
                            icon=icon,
                            machine_name=machine_name,
                            seconds_since_last_contact=seconds_since_last_contact,
                        ),
                    ]
                    + cpu_msgs
                    + ram_msgs
                )
            )

        # Heading in case there is anything to report
        if not messages:
            messages.append("No machines being monitored 😴")

    return messages
