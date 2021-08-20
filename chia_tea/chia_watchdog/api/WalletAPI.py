
class WalletAPI:
    """ This class holds chia information fetched through RPC
    from chia services on the same machine
    """
    # pylint: disable=too-few-public-methods

    is_ready: bool = False
    n_wallets: int = 0
    is_synced: bool = False
    is_running: bool = False

    def copy(self) -> 'WalletAPI':
        """ Get a copy of the instance

        Returns
        -------
        wallet : WalletAPI
            copy of the instance
        """
        new_info = WalletAPI()
        new_info.n_wallets = self.n_wallets
        new_info.is_synced = self.is_synced
        new_info.is_ready = self.is_ready
        new_info.is_running = self.is_running
        return new_info
