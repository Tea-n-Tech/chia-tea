

from typing import Callable, List

from ...protobuf.generated.chia_pb2 import (HarvesterPlot,
                                            HarvesterViewedFromFarmer)
from ...protobuf.generated.computer_info_pb2 import ADD, DELETE, UpdateEvent
from ...protobuf.generated.hardware_pb2 import Disk, Ram
from ...protobuf.to_sqlite.custom import get_update_even_data


def _get_harvester_connection_msg(
    farmer_id: str,
    harvester_id: str,
    ip_address: str,
    is_connected: bool,
) -> str:
    """ Get the connection msg for a harvester

    Parameters
    ----------
    farmer_id : str
        id of the farmer
    harvester_id : str
        id of the harvester
    ip_address : str
        harvester ip address
    is_connected: bool
        connection status

    Returns
    -------
    msg : str
        harvester connection message
    """

    # send message
    icon = "🟢" if is_connected else "🟠"
    connection_status = ("connected"
                         if is_connected
                         else "disconnected")

    CONNECTION_MSG: str = "{icon} Farmer {farmer_id} {status} to Harvester {harvester_id} ({ip})."
    msg = CONNECTION_MSG.format(
        icon=icon,
        harvester_id=harvester_id[:10],
        ip=ip_address,
        status=connection_status,
        farmer_id=farmer_id,
    )

    return msg


def notify_when_farmer_connects_or_disconnects_to_harvester(
        machine_id: str,
        update_events: List[UpdateEvent],
) -> List[str]:
    """ notify when a farmer connected to a farmer

    Parameters
    ----------
    machine_id : str
        id of the machine
    update_events : List[UpdateEvent]
        list of change events which happened

    Returns
    -------
    messages : List[str]
        notification messages
    """
    messages = []

    for event in update_events:
        _, pb_msg = get_update_even_data(event)
        if isinstance(pb_msg, HarvesterViewedFromFarmer):
            if event.event_type in (ADD, DELETE):
                is_connected = event.event_type == ADD
                messages.append(
                    _get_harvester_connection_msg(
                        farmer_id=str(machine_id)[:10],
                        harvester_id=pb_msg.id,
                        ip_address=pb_msg.ip_address,
                        is_connected=is_connected,
                    )
                )

    return messages


def notify_on_full_ram(
        machine_id: str,
        update_events: List[UpdateEvent],
) -> List[str]:
    """ notify if the ram of a machine is full

    Parameters
    ----------
    machine_id : str
        id of the machine
    update_events : List[UpdateEvent]
        list of change events which happened

    Returns
    -------
    messages : List[str]
        notification messages
    """

    messages = []

    # check for messages
    for event in update_events:
        _, pb_msg = get_update_even_data(event)
        if isinstance(pb_msg, Ram):
            ram_usage = pb_msg.used_ram / pb_msg.total_ram
            if ram_usage > 0.95:
                messages.append("⚠️ Machine {machine_id} uses {usage:.1f}% of RAM".format(
                    machine_id=machine_id,
                    usage=ram_usage * 100,
                ))

    return messages


def notify_if_a_disk_is_lost(
    machine_id: str,
    update_events: List[UpdateEvent]
) -> List[str]:
    """ notify if a machine looses a disk

    Parameters
    ----------
    machine_id : str
        id of the machine
    update_events : List[UpdateEvent]
        list of change events which happened

    Returns
    -------
    messages : List[str]
        notification messages
    """

    messages = []
    for event in update_events:
        _, pb_msg = get_update_even_data(event)
        if isinstance(pb_msg, Disk):
            if event.event_type == DELETE:
                messages.append(
                    "⚠️   Machine {machine_id} lost disk {mountpoint}".format(
                        machine_id=machine_id,
                        mountpoint=pb_msg.mountpoint
                    )
                )

    return messages


def notify_if_plots_are_lost(
    machine_id: str,
    update_events: List[UpdateEvent]
) -> List[str]:
    """ notify if a machine looses a disk

    Parameters
    ----------
    machine_id : str
        id of the machine
    update_events : List[UpdateEvent]
        list of change events which happened

    Returns
    -------
    messages : List[str]
        notification messages
    """

    n_deleted_plots = 0
    for event in update_events:
        _, pb_msg = get_update_even_data(event)
        if isinstance(pb_msg, HarvesterPlot):
            if event.event_type == DELETE:
                n_deleted_plots += 1

    messages = []
    if n_deleted_plots:
        messages.append(
            "⚠️ Machine {machine_id} lost {n_plots} plots 🌽".format(
                machine_id=machine_id,
                n_plots=n_deleted_plots
            )
        )

    return messages


def get_update_event_messages_if_any(
    machine_id: str,
    update_events: List[UpdateEvent],
) -> List[str]:
    """ Checks if we need to print any messages regarding harvesters

    Parameters
    ----------
    update_events : List[UpdateEvent]
        update events which happened

    Returns
    -------
    messages : List[str]
        list of messages to print
    """
    messages = []

    for get_msg_fun in ALL_EVENT_OBSERVERS:
        messages += get_msg_fun(machine_id, update_events)

    return messages


ALL_EVENT_OBSERVERS: Callable[[str, List[UpdateEvent]], List[str]] = (
    notify_when_farmer_connects_or_disconnects_to_harvester,
    notify_on_full_ram,
    notify_if_plots_are_lost,
    notify_if_a_disk_is_lost,
)
