import unittest
from datetime import datetime

from chia.server.outbound_message import NodeType

from ...models.ChiaWatchdog import ChiaWatchdog
from ...models.FarmerHarvesterAPI import FarmerHarvesterAPI
from ...models.FarmerHarvesterLogfile import FarmerHarvesterLogfile
from ...protobuf.generated.chia_pb2 import HarvesterViewedFromFarmer
from ...utils.testing import async_test
from .chia import collect_connected_harvesters_to_farmer


class TestChiaDataCollection(unittest.TestCase):
    @async_test
    async def test_farmer_harvester_collection(self):

        node_id = b"1n\x0f\xc4J\xb5q8\xc4\x98\x0b\xe7\\\xac\xd1\x82"
        node_id_str = node_id.hex()
        plots = ["only", "length", "is", "used"]
        creation_time = 1.0
        time_last_msg_received = 2.5
        time_last_msg_sent = 1.5
        ip_address = "127.0.0.2"
        missed_challenges = 3

        harvster_api = FarmerHarvesterAPI(
            node_id=node_id,
            bytes_read=732920,
            bytes_written=736979,
            creation_time=creation_time,
            last_message_time=time_last_msg_received,
            local_port=8447,
            peer_host=ip_address,
            peer_port=51844,
            peer_server_port=8448,
            type=NodeType.HARVESTER.value,
            n_plots=len(plots),
        )
        harvester_logfile = FarmerHarvesterLogfile(
            harvester_id=node_id_str,
            ip_address=ip_address,
            last_update=datetime.fromtimestamp(max(time_last_msg_received, time_last_msg_sent)),
            time_last_incoming_msg=datetime.fromtimestamp(time_last_msg_received),
            time_last_outgoing_msg=datetime.fromtimestamp(time_last_msg_sent),
            time_of_end_of_last_sgn_point=1,
            timed_out=False,
            is_connected=True,
            n_overdue_responses=missed_challenges,
            n_responses=0,
        )

        dog = ChiaWatchdog("", "")
        dog.farmer_service.connections = [harvster_api]
        dog.harvester_infos = {node_id_str: harvester_logfile}

        # do the thing
        harvester_list = await collect_connected_harvesters_to_farmer(dog)

        self.assertTrue(len(harvester_list), 1)
        harvester: HarvesterViewedFromFarmer = harvester_list[0]
        self.assertEqual(harvester.id, node_id_str)
        self.assertEqual(harvester.connection_time, creation_time)
        self.assertEqual(harvester.time_last_msg_received, time_last_msg_received)
        self.assertEqual(harvester.time_last_msg_sent, time_last_msg_sent)
        self.assertEqual(harvester.ip_address, ip_address)
        self.assertEqual(harvester.missed_challenges, missed_challenges)
        self.assertEqual(harvester.n_plots, len(plots))
