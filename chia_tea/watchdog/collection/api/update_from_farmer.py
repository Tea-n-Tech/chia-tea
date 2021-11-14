from typing import Any, Dict, List, Set

from chia.rpc.farmer_rpc_client import FarmerRpcClient
from chia.server.outbound_message import NodeType
from chia.util.config import load_config
from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.ints import uint16

from ....models.ChiaWatchdog import ChiaWatchdog
from ....models.FarmerHarvesterAPI import FarmerHarvesterAPI
from .shared_settings import API_EXCEPTIONS

NODE_ID = "node_id"


async def _update_farmer_connections(
    farmer_client: FarmerRpcClient,
) -> List[FarmerHarvesterAPI]:

    harvesters = []

    # general connection information
    harvester_connections: Dict[str, Dict[str, Any]] = {
        data[NODE_ID].hex(): data
        for data in await farmer_client.get_connections()
        if data.get("type") == NodeType.HARVESTER.value
    }

    # harvester specific data such as plot count
    harvesters_which_disconnected: Set[str] = set()
    response = await farmer_client.get_harvesters()
    if response.get("success"):
        harvester_ids = set()
        harvester_data_list = response.get("harvesters")
        for data in harvester_data_list:
            node_id = data.get("connection").get(NODE_ID)
            harvester_ids.add(node_id)
            n_plots = len(data.get("plots"))
            properties = harvester_connections.get(node_id)

            if properties is not None:
                properties["n_plots"] = n_plots
            else:
                # A new harvester might have connected in-between.
                # We simply skip them.
                pass

        # harvesters which disconnected between the two API calls
        harvesters_which_disconnected = {
            node_id for node_id in harvester_connections.keys() if node_id not in harvester_ids
        }

    for node_id, kwargs in harvester_connections.items():

        # A harvester disconnected inbetween thus we skip it
        if node_id in harvesters_which_disconnected:
            continue

        harvesters.append(FarmerHarvesterAPI(**kwargs))

    return harvesters


async def update_from_farmer(chia_dog: ChiaWatchdog):
    """Updates the chia dog with harvester data

    Parameters
    ----------
    chia_dog : ChiaWatchdog
        watchdog instance to be modified
    """
    # pylint: disable=duplicate-code

    try:
        config = load_config(DEFAULT_ROOT_PATH, "config.yaml", exit_on_error=False)
        self_hostname = config["self_hostname"]
        farmer_rpc_port = config["farmer"]["rpc_port"]
        farmer_client = await FarmerRpcClient.create(
            self_hostname,
            uint16(farmer_rpc_port),
            DEFAULT_ROOT_PATH,
            config,
        )

        chia_dog.farmer_service.connections = await _update_farmer_connections(
            farmer_client=farmer_client,
        )
        chia_dog.farmer_service.is_running = True

    # pylint: disable=catching-non-exception
    except API_EXCEPTIONS:
        chia_dog.farmer_service.connections.clear()
        chia_dog.farmer_service.is_running = False
    finally:
        if "farmer_client" in locals():
            farmer_client.close()
            await farmer_client.await_closed()
        chia_dog.farmer_service.is_ready = True
