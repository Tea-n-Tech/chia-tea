import sqlite3
import traceback
from contextlib import contextmanager
from typing import Generator, List


def catch_errors_as_message(function):
    """Catches errors as a list of messages

    Parameters
    ----------
    function : Coroutine[Any, Any, List[str]]
        Function to wrap. In case of an error
        the message is returned.
    """

    async def wrapper(*args, **kwargs) -> List[str]:
        try:
            return await function(*args, **kwargs)
        except Exception:
            trace = traceback.format_exc()
            return [trace]

    return wrapper


@contextmanager
def open_database_read_only(
    db_filepath: str,
) -> Generator[sqlite3.dbapi2.Cursor, None, None]:
    """Open a sqlite database read only

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
