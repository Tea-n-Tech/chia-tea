from chia.rpc.harvester_rpc_client import HarvesterRpcClient
from chia.util.config import load_config
from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.ints import uint16

from ...utils.logger import log_runtime_async
from ..ChiaWatchdog import ChiaWatchdog
from .shared_settings import API_EXCEPTIONS


@log_runtime_async(__file__)
async def update_from_harvester(chia_dog: ChiaWatchdog):
    """ Updates the chia dog with harvester data

    Parameters
    ----------
    chia_dog : ChiaWatchdog
        watchdog instance to be modified
    """

    try:
        config = load_config(
            DEFAULT_ROOT_PATH, "config.yaml", exit_on_error=False)
        self_hostname = config["self_hostname"]

        harvester_rpc_port = config["harvester"]["rpc_port"]
        harvester_client = await HarvesterRpcClient.create(
            self_hostname, uint16(
                harvester_rpc_port), DEFAULT_ROOT_PATH, config
        )

        # reduce timeout from around 4s to 1s
        # timeout = aiohttp.ClientTimeout(total=1)
        # harvester_client.session._timeout = timeout

        plots_response = await harvester_client.get_plots()
        chia_dog.harvester_service.is_running = True
        if plots_response["success"]:
            chia_dog.harvester_service.plots = plots_response["plots"]
            chia_dog.harvester_service.failed_to_open_filenames = \
                plots_response["failed_to_open_filenames"]
            chia_dog.harvester_service.not_found_filenames = \
                plots_response["not_found_filenames"]

        chia_dog.harvester_service.plot_directories = await harvester_client.get_plot_directories()

    # pylint: disable=catching-non-exception
    except API_EXCEPTIONS:
        chia_dog.harvester_service.is_running = False
    finally:
        if "harvester_client" in locals():
            harvester_client.close()
            await harvester_client.await_closed()
        chia_dog.harvester_service.is_ready = True
