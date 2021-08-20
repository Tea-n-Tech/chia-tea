from typing import Any, Iterable, List, Tuple

from sortedcontainers import SortedSet

from ..protobuf.data_collection.computer_info import collect_computer_info
from ..protobuf.generated.computer_info_pb2 import (_UPDATEEVENT, ADD, DELETE,
                                                    UPDATE, ComputerInfo,
                                                    UpdateEvent)
from .ChiaWatchdog import ChiaWatchdog


def get_event_type(old_msg: Any, new_msg: Any) -> int:
    """ Get the event type depending on the objects

    Parameters
    ----------
    old_msg : Any
        previous state
    new_msg : Any
        new state of the proto message

    Returns
    -------
    event_type : int
        which event type (0=ADD, 1=UPDATE, 2=DELETE)
    """
    if old_msg is None and new_msg is not None:
        return ADD
    if old_msg is not None and new_msg is not None:
        return UPDATE
    return DELETE


async def compare_computer_info(
        old_computer_info: ComputerInfo,
        new_computer_info: ComputerInfo,
) -> UpdateEvent:
    """ Compares to computer infos and emits events of deltas

    Parameters
    ----------
    old_computer_info : ComputerInfo
        first computer info for comparison
    new_computer_info : ComputerInfo
        second computer info for comparison

    Yields
    ------
    udpate_event : UpdateEvent
        change events from old to new
    """

    fields = []
    if old_computer_info is not None:
        fields = old_computer_info.DESCRIPTOR.fields
    if new_computer_info is not None:
        fields = new_computer_info.DESCRIPTOR.fields

    # iterate through computer sub-messages and compare them
    for field in fields:

        # we obviously ignore meta attributes
        if field.name in ("timestamp", "machine_id"):
            continue

        # get instance members
        old_msg_or_list = getattr(old_computer_info, field.name)
        new_msg_or_list = getattr(new_computer_info, field.name)

        # bot are already messages ready to be compared
        if (not isinstance(old_msg_or_list, Iterable) and
                not isinstance(new_msg_or_list, Iterable)):
            old_msg = old_msg_or_list
            new_msg = new_msg_or_list

            if old_msg != new_msg:
                yield create_update_event(
                    old_msg=old_msg,
                    new_msg=new_msg,
                    event_type=get_event_type(
                        old_msg_or_list,
                        new_msg_or_list
                    ),
                )
        # both are lists of messages
        elif (isinstance(old_msg_or_list, Iterable) and
                isinstance(new_msg_or_list, Iterable)):
            old_messages = {
                msg.id: msg for msg in old_msg_or_list
            }
            new_messages = {
                msg.id: msg for msg in new_msg_or_list
            }
            all_ids = SortedSet(old_messages.keys()) | SortedSet(
                new_messages.keys())

            for msg_id in all_ids:
                old_msg = old_messages.get(msg_id)
                new_msg = new_messages.get(msg_id)
                if old_msg != new_msg:
                    yield create_update_event(
                        old_msg=old_msg,
                        new_msg=new_msg,
                        event_type=get_event_type(
                            old_msg,
                            new_msg
                        ),
                    )


def create_update_event(
        old_msg: Any,
        new_msg: Any,
        event_type: int
) -> UpdateEvent:
    """ Creates an update event from the event data

    Parameters
    ----------
    old_msg : Any
        protobuf message object at previous state
    new_msg : Any
        protobuf message object at current state
    event_type : EventType
        whether data was added, updated or removed

    Returns
    -------
    update_event : UpdateEvent
        the event ready to be sent to the server
    """
    event_data = new_msg if event_type != DELETE else old_msg

    for field in _UPDATEEVENT.fields:
        if field.message_type == event_data.DESCRIPTOR:
            kwargs = {
                "event_type": event_type,
                field.name: event_data
            }
            return UpdateEvent(
                **kwargs
            )

    err_msg = ("Could not send update event since the data" +
               " didn't match any type which can be send" +
               f" by the message protocol. Event type was '{event_type}'" +
               f" and data was of type: {type(event_data)}")
    raise RuntimeError(err_msg)


async def get_update_events(
    machine_id: str,
    initial_state: ComputerInfo,
    chia_dog: ChiaWatchdog,
) -> Tuple[List[UpdateEvent], ComputerInfo]:
    """ Get a continuous stream of update events about what is changing

    Parameters
    ----------
    machine_id : str
        id of the machine
    initial_state : ComputerInfo
        initial state given by the server
    chia_dog : ChiaWatchdog

    Yields
    ------
    update_events : List[UpdateEvent]
        changes happening on the machine
    current_state : ComputerInfo
        current state of the computer
    """

    new_computer_info = await collect_computer_info(machine_id, chia_dog)

    update_events = [
        change_event
        async for change_event in compare_computer_info(
            old_computer_info=initial_state,
            new_computer_info=new_computer_info
        )
    ]

    return update_events, new_computer_info
