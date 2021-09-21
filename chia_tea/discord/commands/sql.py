
import sqlite3
from io import StringIO
from typing import Iterable, List

from rich.console import Console
from rich.table import Table

from ..common import catch_errors_as_message, open_database_read_only


ROW_LIMIT = 5


async def format_sql_rows(rows: list, names: Iterable[str]) -> List[str]:
    """ Format the sql rows as a table

    Parameters
    ----------
    rows : list
        row values as list
    names : Iterable[str]
        names of the columns

    Returns
    -------
    messages : List[str]
        list of messages to print
    """
    messages = []

    table = Table()

    n_rows = min(len(rows), ROW_LIMIT)

    # format table
    console = Console(file=StringIO())
    # column names
    for name in names:
        table.add_column(name)
    # row values
    for i_row, row in enumerate(rows):
        if i_row > n_rows:
            break
        table.add_row(*tuple(str(value) for value in row))
    console.print(table)

    messages.append("```")
    # pylint: disable=no-member
    messages.append(console.file.getvalue())
    messages.append("```")

    if len(rows) > ROW_LIMIT:
        messages.append(
            f"⚠️ Displaying only {ROW_LIMIT} of {len(rows)} entries.")

    return messages


@catch_errors_as_message
async def sql_cmd(db_filepath: str, cmds: Iterable[str]) -> List[str]:
    """ Execute an sql command and return the results as text

    Parameters
    ----------
    db_filepath : str
        filepath to the database
    cmds : Iterable[str]
        sql commands as iterable

    Returns
    -------
    messages : List[str]
        list of messages to print
    """

    messages = []

    cmd = " ".join(cmds)

    with open_database_read_only(db_filepath) as cursor:
        sql_cursor: sqlite3.Cursor = cursor

        sql_cursor.execute(cmd)
        rows = sql_cursor.fetchall()

        # this contains the names but if nothing is
        # found this is none
        description = sql_cursor.description or tuple()
        entry_names = tuple(
            entry[0]
            for entry in description
        )

        messages += await format_sql_rows(rows, entry_names)

    if not messages:
        messages.append("😐 No entries found ")

    return messages
