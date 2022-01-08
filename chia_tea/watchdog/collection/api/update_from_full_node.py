from chia.rpc.full_node_rpc_client import FullNodeRpcClient
from chia.util.config import load_config
from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.ints import uint16


from ....models.ChiaWatchdog import ChiaWatchdog
from ....utils.logger import log_runtime_async
from .shared_settings import API_EXCEPTIONS


@log_runtime_async(__file__)
async def update_from_full_node(chia_dog: ChiaWatchdog):
    """Updates the chia dog with full_node data

    Parameters
    ----------
    chia_dog : ChiaWatchdog
        watchdog instance to be modified

    Example Response
    ----------------
        {
            'difficulty': 7,
            'genesis_challenge_initialized': True,
            'mempool_size': 0,
            'peak': None,
            'space': 0,
            'sub_slot_iters': 134217728,
            'sync': {
                'sync_mode': True,
                'sync_progress_height': 0,
                'sync_tip_height': 1390736,
                'synced': False
            }
        }

    """

    try:
        config = load_config(DEFAULT_ROOT_PATH, "config.yaml", exit_on_error=False)
        self_hostname = config["self_hostname"]

        full_node_rpc_port = config["full_node"]["rpc_port"]
        full_node_client = await FullNodeRpcClient.create(
            self_hostname, uint16(full_node_rpc_port), DEFAULT_ROOT_PATH, config
        )

        state_dict = await full_node_client.get_blockchain_state()
        sync_dict = state_dict.get("sync", {})
        is_synced = sync_dict.get("synced", False)
        sync_blockchain_height = sync_dict.get("sync_tip_height", 0)
        sync_progress_height = sync_dict.get("sync_progress_height", 0)

        chia_dog.full_node_service.is_running = True
        chia_dog.full_node_service.is_synced = is_synced
        chia_dog.full_node_service.sync_blockchain_height = sync_blockchain_height
        chia_dog.full_node_service.sync_progress_height = sync_progress_height

    # pylint: disable=catching-non-exception
    except API_EXCEPTIONS:
        chia_dog.full_node_service.is_running = False
    finally:
        if "full_node_client" in locals():
            full_node_client.close()
            await full_node_client.await_closed()
        chia_dog.full_node_service.is_ready = True
