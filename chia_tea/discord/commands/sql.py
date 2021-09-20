
import sqlite3
from io import StringIO
from typing import Iterable, List

from rich.console import Console
from rich.table import Table

from ..common import catch_errors_as_message, open_database_read_only


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
    table = Table()

    with open_database_read_only(db_filepath) as cursor:
        sql_cursor: sqlite3.Cursor = cursor

        sql_cursor.execute(cmd)
        rows = sql_cursor.fetchall()
        row_limit = 5
        n_rows = min(len(rows), row_limit)
        has_too_many_rows = len(rows) > row_limit

        # this contains the names but if nothing is
        # found this is none
        description = cursor.description or tuple()
        entry_names = tuple(
            entry[0]
            for entry in description
        )

        # format table
        console = Console(file=StringIO())
        for name in entry_names:
            table.add_column(name)

        for i_row, row in enumerate(rows):
            if i_row > n_rows:
                break
            table.add_row(*tuple(str(value) for value in row))
        console.print(table)
        messages.append("```")
        messages.append(console.file.getvalue())
        messages.append("```")
        if has_too_many_rows:
            messages.append(
                f"⚠️ Displaying only {row_limit} of {len(rows)} entries.")

    if not messages:
        messages.append("😐 No entries found ")

    return messages
