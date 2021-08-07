
class WalletAPI:
    is_ready: bool = False
    n_wallets: int = 0
    is_synced: bool = False
    is_running: bool = False

    def copy(self) -> 'WalletAPI':
        new_info = WalletAPI()
        new_info.n_wallets = self.n_wallets
        new_info.is_synced = self.is_synced
        new_info.is_ready = self.is_ready
        new_info.is_running = self.is_running
        return new_info
