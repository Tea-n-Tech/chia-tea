

from typing import List

from sortedcontainers import SortedSet

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

    old_n_proofs = old_computer_info.harvester_info.n_proofs
    new_n_proofs = new_computer_info.harvester_info.n_proofs

    if old_n_proofs < new_n_proofs:
        messages.append(
            "{icon}   Harvester {machine_name} {status}.".format(
                icon="🔍",
                machine_name=get_machine_info_name(machine),
                status="found a proof"
            )
        )

    return messages


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
    messages = []
    old_harvesters = {
        harvester.id: harvester
        for harvester in old_computer_info.connected_harvesters
    }
    new_harvesters = {
        harvester.id: harvester
        for harvester in new_computer_info.connected_harvesters
    }
    all_ids = SortedSet(old_harvesters.keys()).union(
        SortedSet(new_harvesters.keys())
    )
    default_harvester = HarvesterViewedFromFarmer()
    for harvester_id in all_ids:
        old_harvester = old_harvesters.get(harvester_id, default_harvester)
        new_harvester = new_harvesters.get(harvester_id, default_harvester)
        if new_harvester.n_timeouts > old_harvester.n_timeouts:
            messages.append(
                "{icon}   Harvester {machine_name} {status}.".format(
                    icon="👴🏻",
                    machine_name=get_machine_info_name(machine),
                    status="timed out"
                )
            )

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

    old_wallet_synced = old_computer_info.wallet_info.is_synced
    new_wallet_synced = new_computer_info.wallet_info.is_synced

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

    old_wallet_connected = old_computer_info.wallet_info.is_running
    new_wallet_connected = new_computer_info.wallet_info.is_running

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
