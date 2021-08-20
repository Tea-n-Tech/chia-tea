

from datetime import datetime
from typing import List

from ...protobuf.generated.chia_pb2 import HarvesterViewedFromFarmer
from ...protobuf.generated.computer_info_pb2 import ComputerInfo
from ...protobuf.generated.machine_info_pb2 import MachineInfo
from .common import get_machine_info_name


def notify_on_harvester_reward_found(
    machine: MachineInfo,
    old_computer_info: ComputerInfo,
    new_computer_info: ComputerInfo,
) -> List[str]:
    """ notify when a reward was found

    Parameters
    ----------
    machine : MachineInfo
        latest information about the machine
    old_computer_info : ComputerInfo
        computer info before last update
    new_computer_info : ComputerInfo
        computer info after last update

    Returns
    -------
    messages : List[str]
        notification messages
    """

    messages = []

    old_n_proofs = old_computer_info.harvester.n_proofs
    new_n_proofs = new_computer_info.harvester.n_proofs

    if old_n_proofs < new_n_proofs:
        messages.append(
            "{icon}   Harvester {machine_name} {status}.".format(
                icon="🔍",
                machine_name=get_machine_info_name(machine),
                status="found a proof"
            )
        )

    return messages


HARVESTER_TIMOUT = 60  # seconds
timestamp_of_last_timeout_check = 0.


def get_msg_if_farmer_harvester_timed_out(
    machine: MachineInfo,
    last_timestamp: float,
    new_timestamp: float,
    harvester: HarvesterViewedFromFarmer
) -> str:
    """ Returns a message if a farmer recognizes that a harvester
    didn't respond for a while

    Parameters
    ----------
    machine : MachineInfo
        info about the machine itself
    last_timestamp : float
        timestamp when the last time this check was performed
    new_timestamp : float
        timestamp now
    harvester : HarvesterViewedFromFarmer
        harvester to perform timeout check on

    Returns
    -------
    msg : str
        Timeout message or an empty string if the harvester
        didn't time out.
    """

    new_harvester_timed_out = (new_timestamp -
                               harvester.time_last_msg_received >= HARVESTER_TIMOUT)
    previously_notified = (
        last_timestamp - harvester.time_last_msg_received >= HARVESTER_TIMOUT
        # we assume on startup that we already notified on a timeout
        # otherwise we can a message all the time when we restart
        # the bot.
        if last_timestamp != 0.
        else True
    )

    if new_harvester_timed_out and not previously_notified:
        return "{icon}  Harvester {machine_name} {status}.".format(
            icon="⚠️",
            machine_name=get_machine_info_name(machine),
            status=f"didn't respond for {HARVESTER_TIMOUT}s"
        )

    return ""


def notify_when_harvester_times_out(
    machine: MachineInfo,
    old_computer_info: ComputerInfo,
    new_computer_info: ComputerInfo,
) -> List[str]:
    """ notify when a harvester times out

    Parameters
    ----------
    machine_id : str
        id of the machine
    old_computer_info : ComputerInfo
        computer info before last update
    new_computer_info : ComputerInfo
        computer info after last update

    Returns
    -------
    messages : List[str]
        notification messages
    """
    # pylint: disable=unused-argument

    messages = []

    # pylint: disable=global-statement
    global timestamp_of_last_timeout_check
    now = datetime.now().timestamp()

    for harvester in new_computer_info.farmer_harvesters:
        msg = get_msg_if_farmer_harvester_timed_out(
            machine,
            last_timestamp=timestamp_of_last_timeout_check,
            new_timestamp=now,
            harvester=harvester,
        )
        if msg:
            messages.append(msg)

    timestamp_of_last_timeout_check = now

    return messages


def notify_on_wallet_sync_change(
    machine: MachineInfo,
    old_computer_info: ComputerInfo,
    new_computer_info: ComputerInfo,
) -> List[str]:
    """ notify when a wallet is not synced anymore

    Parameters
    ----------
    machine : MachineInfo
        latest information about the machine
    old_computer_info : ComputerInfo
        computer info before last update
    new_computer_info : ComputerInfo
        computer info after last update

    Returns
    -------
    messages : List[str]
        notification messages
    """

    messages = []

    old_wallet_synced = old_computer_info.wallet.is_synced
    new_wallet_synced = new_computer_info.wallet.is_synced

    if not old_wallet_synced and new_wallet_synced:
        messages.append(
            "{machine_name}: ✔️ The wallet 👛 has synced.".format(
                machine_name=get_machine_info_name(machine),
            )
        )
    elif old_wallet_synced and not new_wallet_synced:
        messages.append(
            "{machine_name}: ⚠ The wallet 👛 is not synced anymore".format(
                machine_name=get_machine_info_name(machine),
            )
        )

    return messages


def notify_on_wallet_connection_change(
    machine: MachineInfo,
    old_computer_info: ComputerInfo,
    new_computer_info: ComputerInfo,
) -> List[str]:
    """ notify when a wallet connects or disconnects

    Parameters
    ----------
    machine : MachineInfo
        latest information about the machine
    old_computer_info : ComputerInfo
        computer info before last update
    new_computer_info : ComputerInfo
        computer info after last update

    Returns
    -------
    messages : List[str]
        notification messages
    """

    messages = []

    old_wallet_connected = old_computer_info.wallet.is_running
    new_wallet_connected = new_computer_info.wallet.is_running

    if not old_wallet_connected and new_wallet_connected:
        messages.append(
            "{machine_name}: ✔️ Connected to wallet 👛".format(
                machine_name=get_machine_info_name(machine),
            )
        )
    elif old_wallet_connected and not new_wallet_connected:
        messages.append(
            "{machine_name}: Lost connection to wallet 👛".format(
                machine_name=get_machine_info_name(machine),
            )
        )

    return messages


def get_computer_info_messages_if_any(
    machine: MachineInfo,
    old_computer_info: ComputerInfo,
    new_computer_info: ComputerInfo,
) -> List[str]:
    """ Checks if we need to print any messages regarding harvesters

    Parameters
    ----------
    machine : MachineInfo
        info about the machine
    old_computer_info : ComputerInfo
        computer info before last update
    new_computer_info : ComputerInfo
        computer info after last update

    Returns
    -------
    messages : List[str]
        list of messages to print
    """
    messages = []

    for get_msg_fun in ALL_EVENT_OBSERVERS:
        messages += get_msg_fun(
            machine,
            old_computer_info,
            new_computer_info
        )

    return messages


ALL_EVENT_OBSERVERS = (
    notify_on_harvester_reward_found,
    notify_on_wallet_connection_change,
    notify_on_wallet_sync_change,
    notify_when_harvester_times_out
)
