
from typing import Any, Dict, List

from chia.rpc.farmer_rpc_client import FarmerRpcClient
from chia.server.outbound_message import NodeType
from chia.util.config import load_config
from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.ints import uint16

from ..ChiaWatchdog import ChiaWatchdog
from .FarmerHarvesterAPI import FarmerHarvesterAPI
from .shared_settings import API_EXCEPTIONS


async def _get_farmer_harvesters(
    farmer_client: FarmerRpcClient,
) -> List[FarmerHarvesterAPI]:

    harvesters = []

    # general connection information
    harvester_kwargs: Dict[str, Dict[str, Any]] = {
        kwargs["node_id"].hex(): kwargs
        for kwargs in await farmer_client.get_connections()
        if kwargs.get("type") == NodeType.HARVESTER.value
    }

    # harvester specific data such as plot count
    response = await farmer_client.get_harvesters()
    if response.get("success"):
        for kwargs in response.get("harvesters"):
            node_id = kwargs.get("connection").get("node_id")
            n_plots = len(kwargs.get("plots"))
            harvester_kwargs[node_id]["n_plots"] = n_plots

    for kwargs in harvester_kwargs.values():
        harvesters.append(
            FarmerHarvesterAPI(
                **kwargs
            )
        )

    return harvesters


async def update_from_farmer(chia_dog: ChiaWatchdog):
    """ Updates the chia dog with harvester data

    Parameters
    ----------
    chia_dog : ChiaWatchdog
        watchdog instance to be modified
    """
    # pylint: disable=duplicate-code

    try:
        config = load_config(
            DEFAULT_ROOT_PATH, "config.yaml", exit_on_error=False)
        self_hostname = config["self_hostname"]
        farmer_rpc_port = config["farmer"]["rpc_port"]
        farmer_client = await FarmerRpcClient.create(
            self_hostname,
            uint16(farmer_rpc_port),
            DEFAULT_ROOT_PATH,
            config,
        )

        chia_dog.farmer_service.connections = await _get_farmer_harvesters(
            farmer_client=farmer_client
        )
        chia_dog.farmer_service.is_running = True

    # pylint: disable=catching-non-exception
    except API_EXCEPTIONS:
        chia_dog.farmer_service.connections = []
        chia_dog.farmer_service.is_running = False
    finally:
        if "farmer_client" in locals():
            farmer_client.close()
            await farmer_client.await_closed()
        chia_dog.farmer_service.is_ready = True
