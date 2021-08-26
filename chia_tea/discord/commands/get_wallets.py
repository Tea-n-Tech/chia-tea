
from typing import List

from discord.ext.commands import Context

from ...utils.config import get_config
from ..common import (catch_errors_as_message, get_machine_info_name,
                      open_database_read_only)
from ..notifications.run_notifiers import \
    get_current_computer_and_machine_infos_from_db


@catch_errors_as_message
async def wallets_cmd(ctx: Context) -> List[str]:
    """ Formats all wallets into a message

    Parameters
    ----------
    ctx : Context
        discord context

    Returns
    -------
    messages : List[str]
        list of messages to print
    """
    messages = []

    db_filepath = get_config().monitoring.server.db_filepath

    with open_database_read_only(db_filepath) as cursor:
        machine_and_computer_info_dict = get_current_computer_and_machine_infos_from_db(
            cursor
        )
        messages = []

        for _, (machine, computer_info) in machine_and_computer_info_dict.items():
            wallet = computer_info.wallet
            if wallet.is_running:
                icon = "🟢" if wallet.is_synced else "🟠"
                not_msg = "" if wallet.is_synced else "not "
                messages.append(
                    f"\nWallet 👛 *{get_machine_info_name(machine)}*")
                messages.append(f"   {icon} {not_msg}synchronized")

        # Heading in case there is anything to report
        if not messages:
            messages.append("No wallets 👛 found.")

    return messages
