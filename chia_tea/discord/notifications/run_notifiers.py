
import asyncio
import logging
import sqlite3
import traceback
from datetime import datetime
from typing import Dict, List, Tuple

import discord

from ...protobuf.generated.computer_info_pb2 import ComputerInfo
from ...protobuf.generated.machine_info_pb2 import MachineInfo
from ...protobuf.to_sqlite.sql_cmds import (get_computer_info_from_db,
                                            get_machine_infos_from_db,
                                            get_update_events_from_db)
from ...utils.logger import get_logger
from .common import open_database_read_only
from .computer_info_notifications import get_computer_info_messages_if_any
from .update_event_notifications import get_update_event_messages_if_any


async def log_and_send_msg_if_any(
    messages: List[str],
    logger: logging.Logger,
    channel: discord.ChannelType,
    is_testing: bool,
):
    """ Logs and sends the messages if not empty

    Parameters
    ----------
    messages : List[str]
        messages to print
    logger : logging.Logger
        logger for printing
    channel : discord.ChannelType
        discord channel to send messages to
    is_testing : bool
        whether to run in testing mode and not
        send but log messages
    """
    if messages:
        total_message = "\n".join(messages)
        logger.info(total_message)
        if not is_testing:
            await channel.send(total_message)


def get_current_computer_and_machine_infos_from_db(
        cursor: sqlite3.Cursor
) -> Dict[str, Tuple[MachineInfo, ComputerInfo]]:
    """ Get all current computer infos from the database

    Parameters
    ----------
    cursor: sqlite3.Cursor
        cursor to the sqlite3 db

    Returns
    -------
    computer_and_machine_infos : Dict[str, Tuple[MachineInfo, ComputerInfo]]
        dict with machine and computer info as value and machine
        id as key
    """
    machine_info_list, _ = get_machine_infos_from_db(cursor)

    computer_and_machine_infos = {}
    for machine in machine_info_list:
        computer_and_machine_infos[machine.machine_id] = \
            (
                machine,
                get_computer_info_from_db(
                    cursor,
                    machine.machine_id,
                )
        )

    return computer_and_machine_infos


async def run_notifiers(
    db_filepath: str,
    channel: discord.ChannelType,
    is_testing: bool,
):
    """ Notify channel in case a harvester got lost

    Parameters
    ----------
    db_filepath : str
        path to the monitoring db
    channel : discord.ChannelType
        discord channel for notifications
    is_testing : bool
        whether to run in testing mode and not
        send but log messages
    """
    # pylint: disable=too-many-locals

    logger = get_logger(__name__)

    # time for a looping
    while True:
        try:

            with open_database_read_only(db_filepath) as cursor:

                # fetch the state of all machines last known
                old_machine_computer_info_dict = get_current_computer_and_machine_infos_from_db(
                    cursor
                )

                last_timestamp = int(datetime.now().timestamp())
                while True:

                    # wait inbetween status checks, no need to go crazy
                    # also kind of nice since the bot does not enrage
                    wait_time_between_checks = 2
                    await asyncio.sleep(wait_time_between_checks)

                    new_timestamp = int(datetime.now().timestamp())
                    messages = []

                    # messages related to update events
                    machine_events = get_update_events_from_db(
                        cursor,
                        last_timestamp,
                        new_timestamp,
                    )

                    for machine_id, event_list in machine_events.items():
                        messages += get_update_event_messages_if_any(
                            machine_id,
                            event_list,
                        )

                    # messages by computer info comparison
                    new_machine_computer_info_dict = get_current_computer_and_machine_infos_from_db(
                        cursor,
                    )

                    for machine_id, (machine_info, new_computer_info) \
                            in new_machine_computer_info_dict.items():
                        _, old_computer_info = old_machine_computer_info_dict.get(
                            machine_id,
                            ComputerInfo(),
                        )
                        new_computer_info = get_computer_info_from_db(
                            cursor,
                            machine_id,
                        )
                        messages += get_computer_info_messages_if_any(
                            machine=machine_info,
                            old_computer_info=old_computer_info,
                            new_computer_info=new_computer_info,
                        )

                    # print message if any
                    await log_and_send_msg_if_any(
                        messages=messages,
                        logger=logger,
                        channel=channel,
                        is_testing=is_testing,
                    )

                    # if all went fine we can update the last timestamp
                    last_timestamp = new_timestamp
                    # and the last known state
                    old_machine_computer_info_dict = new_machine_computer_info_dict

        # something on db level failed
        except Exception:
            tb = traceback.format_exc()
            get_logger(__file__).error(tb)

            await asyncio.sleep(2)
