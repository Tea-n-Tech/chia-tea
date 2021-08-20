from chia.rpc.wallet_rpc_client import WalletRpcClient
from chia.util.config import load_config
from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.ints import uint16

from ..ChiaWatchdog import ChiaWatchdog
from .shared_settings import API_EXCEPTIONS


async def update_from_wallet(chia_dog: ChiaWatchdog):
    """ Updates the chia dog with wallet data

    Parameters
    ----------
    chia_dog : ChiaWatchdog
        watchdog instance to be modified
    """

    try:
        config = load_config(
            DEFAULT_ROOT_PATH, "config.yaml", exit_on_error=False)
        self_hostname = config["self_hostname"]
        wallet_rpc_port = config["wallet"]["rpc_port"]

        wallet_client = await WalletRpcClient.create(
            self_hostname,
            uint16(wallet_rpc_port),
            DEFAULT_ROOT_PATH,
            config
        )

        # reduce timeout from around 4s to 1s
        # timeout = aiohttp.ClientTimeout(total=1)
        # wallet_client.session._timeout = timeout

        chia_dog.wallet_service.n_wallets = len(await wallet_client.get_connections())
        chia_dog.wallet_service.is_running = True
        chia_dog.wallet_service.is_synced = await wallet_client.get_synced()

    # pylint: disable=catching-non-exception
    except API_EXCEPTIONS:
        chia_dog.wallet_service.n_wallets = 0
        chia_dog.wallet_service.is_running = False
        chia_dog.wallet_service.is_synced = False
    finally:
        if "wallet_client" in locals():
            wallet_client.close()
            await wallet_client.await_closed()
        chia_dog.wallet_service.is_ready = True
