from typing import Dict, List

from chia.rpc.farmer_rpc_client import FarmerRpcClient
from chia.server.outbound_message import NodeType
from chia.util.config import load_config
from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.ints import uint16

from ..ChiaWatchdog import ChiaWatchdog
from .FarmerHarvesterAPI import FarmerHarvesterAPI
from .shared_settings import API_EXCEPTIONS

NODE_ID = "node_id"


async def _update_farmer_connections(
    farmer_client: FarmerRpcClient,
    farmer_harvesters: List[FarmerHarvesterAPI],
) -> None:

    # IMPORTANT:
    # We mutate existing data objects if possible
    # to avoid bugs with wrong data references.
    # It is a pain in the butt though.

    previous_harvesters = {harvester.node_id: harvester for harvester in farmer_harvesters}

    # fetches general connection data from the farmer
    connection_data = await farmer_client.get_connections()

    # filter harvesters from all connections
    connected_harvesters = {
        data[NODE_ID]: data for data in connection_data if data["type"] == NodeType.HARVESTER.value
    }

    # change values of existing harvesters
    for node_id, data in connected_harvesters.items():
        old_harvester = previous_harvesters.get(node_id)
        if old_harvester is not None:
            for field_name, field_value in data.items():
                # This is a hack to catch an error in case the API changed names
                # and the attribute names don't match anymore.
                getattr(old_harvester, field_name)
                setattr(old_harvester, field_name, field_value)

    # create the new harvesters which have connected
    new_harvesters: Dict[bytes, FarmerHarvesterAPI] = {
        node_id: FarmerHarvesterAPI(**data)
        for node_id, data in connected_harvesters.items()
        if node_id not in previous_harvesters
    }

    # harvesters which disconnected
    harvesters_to_remove = [
        i_harvester
        for i_harvester, harvester in enumerate(farmer_harvesters)
        if harvester.node_id not in connected_harvesters
    ]

    # harvester specific data such as plot count
    all_harvesters = {**new_harvesters, **previous_harvesters}
    response = await farmer_client.get_harvesters()
    if response.get("success"):
        for kwargs in response.get("harvesters"):
            node_id = kwargs.get("connection").get(NODE_ID)

            # There might have been changes on the server
            # thus it is not guaranteed that we find every
            # harvester on the other side after the second
            # call.
            harvester = all_harvesters.get(node_id)
            if harvester:
                harvester.n_plots = len(kwargs.get("plots"))

    # apply changes to existing list
    for i_harvester in reversed(harvesters_to_remove):
        farmer_harvesters.pop(i_harvester)
    for harvester in new_harvesters.values():
        farmer_harvesters.append(harvester)


async def update_from_farmer(chia_dog: ChiaWatchdog):
    """Updates the chia dog with harvester data

    Parameters
    ----------
    chia_dog : ChiaWatchdog
        watchdog instance to be modified
    """
    # pylint: disable=duplicate-code,too-many-locals

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

        await _update_farmer_connections(
            farmer_client=farmer_client,
            farmer_harvesters=chia_dog.farmer_service.connections,
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
