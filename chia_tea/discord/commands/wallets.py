from typing import List

from ..common import catch_errors_as_message, open_database_read_only
from ..formatting import get_machine_info_name
from ..notifications.run_notifiers import get_current_computer_and_machine_infos_from_db


@catch_errors_as_message
async def wallets_cmd(db_filepath: str) -> List[str]:
    """Formats all wallets into a message

    Parameters
    ----------
    db_filepath : str
        path to the sqlite database

    Returns
    -------
    messages : List[str]
        list of messages to print
    """
    messages = []

    with open_database_read_only(db_filepath) as cursor:
        machine_and_computer_info_dict = get_current_computer_and_machine_infos_from_db(cursor)
        messages = []

        for _, (machine, computer_info) in machine_and_computer_info_dict.items():
            wallet = computer_info.wallet
            if wallet.is_running:
                icon = "🟢" if wallet.is_synced else "🟠"
                not_msg = "" if wallet.is_synced else "not "
                messages.append(
                    "\n".join(
                        (
                            f"Wallet 👛 *{get_machine_info_name(machine)}*",
                            f"   {icon} {not_msg}synchronized",
                        )
                    )
                )

        # Heading in case there is anything to report
        if not messages:
            messages.append("No wallets 👛 found.")

    return messages
