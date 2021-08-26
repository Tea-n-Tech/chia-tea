
import sqlite3
import traceback
from contextlib import contextmanager
from typing import Generator, List

from ..protobuf.generated.machine_info_pb2 import MachineInfo


async def catch_errors_as_message(function):
    """ Catches errors as a list of messages

    Parameters
    ----------
    function : Callable
        Function to wrap. In case of an error
        the message is returned.
    """
    async def wrapper(*args, **kwargs):
        try:
            return await function(*args, **kwargs)
        except:
            trace = traceback.format_exc()
            return [trace]
    return wrapper


@contextmanager
def open_database_read_only(
    db_filepath: str
) -> Generator[sqlite3.dbapi2.Cursor, None, None]:
    """ Open a sqlite database read only

    Parameters
    ----------
    db_filepath : str
        filepath to database

    Returns
    -------
    connection : sqlite3.Connection
        connection object
    cursor : sqlite3.Cursor
        sqlite cursor
    """
    try:
        connection = sqlite3.connect(
            f"file:{db_filepath}?mode=ro",
            uri=True,
        )
        cursor = connection.cursor()
        yield cursor
    finally:
        connection.commit()
        connection.close()


def get_machine_info_name(machine: MachineInfo) -> str:
    """ Get a nicely formatted name for a machine info

    Parameters
    ----------
    machine : MachineInfo
        machine info to get a name of

    Returns
    -------
    name : str
        nicely formatted name of the machine info
    """

    return "{name} {id} ({ip})".format(
        name=f"{machine.name} -" if machine.name else "",
        id=str(machine.machine_id)[:10],
        ip=machine.ip_address,
    )
