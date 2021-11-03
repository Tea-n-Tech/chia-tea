import sqlite3
from io import StringIO
from typing import Iterable, List

from rich.console import Console
from rich.table import Table

from ..common import catch_errors_as_message, open_database_read_only

ROW_LIMIT = 5


async def format_sql_rows(rows: list, names: Iterable[str]) -> str:
    """Format the sql rows as a table

    Parameters
    ----------
    rows : list
        row values as list
    names : Iterable[str]
        names of the columns

    Returns
    -------
    msg : str
        msg to print
    """
    msg = ""

    table = Table()

    n_rows = min(len(rows), ROW_LIMIT)
    if not n_rows:
        return msg

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

    # pylint: disable=no-member
    output = console.file.getvalue()
    msg += f"```\n{output}```"

    if len(rows) > ROW_LIMIT:
        msg += f"\n⚠️ Displaying only {ROW_LIMIT} of {len(rows)} entries."

    return msg


@catch_errors_as_message
async def sql_cmd(db_filepath: str, cmd: str) -> List[str]:
    """Execute an sql command and return the results as text

    Parameters
    ----------
    db_filepath : str
        filepath to the database
    cmds : str
        sql command

    Returns
    -------
    messages : List[str]
        list of messages to print
    """

    messages = []

    with open_database_read_only(db_filepath) as cursor:
        sql_cursor: sqlite3.Cursor = cursor
        try:
            sql_cursor.execute(cmd)
            rows = sql_cursor.fetchall()

            # this contains the names but if nothing is
            # found this is none
            description = sql_cursor.description or tuple()
            entry_names = tuple(entry[0] for entry in description)

            msg = await format_sql_rows(rows, entry_names)
            if msg:
                messages.append(msg)

        except sqlite3.OperationalError as err:
            messages.append(str(err))

    if not messages:
        messages.append("😐 No entries found ")

    return messages
