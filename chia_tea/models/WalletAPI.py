from dataclasses import dataclass


@dataclass
class WalletAPI:
    """This class holds chia information fetched through RPC
    from chia services on the same machine
    """

    # pylint: disable=too-few-public-methods

    is_ready: bool = False
    n_wallets: int = 0
    is_synced: bool = False
    is_running: bool = False
