import unittest
from unittest import mock
from chia.server.outbound_message import NodeType

from chia_tea.chia_watchdog.api.FarmerHarvesterAPI import FarmerHarvesterAPI


from ..ChiaWatchdog import ChiaWatchdog
from ...utils.testing import async_test

from .update_from_farmer import update_from_farmer


class TestUpdatingFromFarmer(unittest.TestCase):
    @async_test
    @mock.patch("chia_tea.chia_watchdog.api.update_from_farmer.FarmerRpcClient", autospec=True)
    async def test_new_harvester_connected(self, MockRpcClient):
        dog = ChiaWatchdog("", "")

        node_id = b"1n\x0f\xc4J\xb5q8\xc4\x98\x0b\xe7\\\xac\xd1\x82..."
        plots = ["only", "length", "is", "used"]

        connection_result = {
            "bytes_read": 732920,
            "bytes_written": 736979,
            "creation_time": 1625781881.464225,
            "last_message_time": 1625856666.3932514,
            "local_port": 8447,
            "node_id": node_id,
            "peer_host": "127.0.0.1",
            "peer_port": 51844,
            "peer_server_port": 8448,
            "type": NodeType.HARVESTER.value,
        }
        harvester_result = {
            "success": True,
            "harvesters": [
                {"plots": plots, "connection": {"node_id": node_id}},
            ],
        }

        MockRpcClient = MockRpcClient.create.return_value
        MockRpcClient.get_connections.return_value = [connection_result]
        MockRpcClient.get_harvesters.return_value = harvester_result
        MockRpcClient.close.return_value = None
        MockRpcClient.await_closed.return_value = None

        # do the thing
        await update_from_farmer(dog)

        # validate
        self.assertTrue(MockRpcClient.get_connections.called)
        self.assertTrue(MockRpcClient.get_harvesters.called)
        self.assertTrue(MockRpcClient.close.called)
        self.assertTrue(MockRpcClient.await_closed.called)

        harvester_list = dog.farmer_service.connections
        self.assertEqual(len(harvester_list), 1)

        harvester = harvester_list[0]
        for name, value in connection_result.items():
            self.assertEqual(
                value,
                getattr(harvester, name),
                "Harvester attribute '%s' does not match" % name,
            )
        self.assertEqual(harvester.n_plots, len(plots))

    @async_test
    @mock.patch("chia_tea.chia_watchdog.api.update_from_farmer.FarmerRpcClient", autospec=True)
    async def test_harvester_disconnected(self, MockRpcClient):
        dog = ChiaWatchdog("", "")

        node_id = b"1n\x0f\xc4J\xb5q8\xc4\x98\x0b\xe7\\\xac\xd1\x82..."
        dog.farmer_service.connections = [
            FarmerHarvesterAPI(
                node_id=node_id,
                bytes_read=732920,
                bytes_written=736979,
                creation_time=1625781881.464225,
                last_message_time=1625856666.3932514,
                local_port=8447,
                peer_host="127.0.0.1",
                peer_port=51844,
                peer_server_port=8448,
                type=NodeType.HARVESTER.value,
            )
        ]
        previous_list = dog.farmer_service.connections
        harvester_result = {
            "success": True,
            "harvesters": [],
        }

        MockRpcClient = MockRpcClient.create.return_value
        MockRpcClient.get_connections.return_value = []
        MockRpcClient.get_harvesters.return_value = harvester_result
        MockRpcClient.close.return_value = None
        MockRpcClient.await_closed.return_value = None

        # do the thing
        await update_from_farmer(dog)

        # validate
        self.assertTrue(MockRpcClient.get_connections.called)
        self.assertTrue(MockRpcClient.get_harvesters.called)
        self.assertTrue(MockRpcClient.close.called)
        self.assertTrue(MockRpcClient.await_closed.called)

        harvester_list = dog.farmer_service.connections
        self.assertEqual(len(harvester_list), 0)
        self.assertIs(previous_list, dog.farmer_service.connections)

    @async_test
    @mock.patch("chia_tea.chia_watchdog.api.update_from_farmer.FarmerRpcClient", autospec=True)
    async def test_existing_harvester_is_updated(self, MockRpcClient):
        dog = ChiaWatchdog("", "")

        node_id = b"1n\x0f\xc4J\xb5q8\xc4\x98\x0b\xe7\\\xac\xd1\x82..."
        plots = ["only", "length", "is", "used"]
        old_harvester = FarmerHarvesterAPI(
            node_id=node_id,
            bytes_read=732920,
            bytes_written=736979,
            creation_time=1625781881.464225,
            last_message_time=1625856666.3932514,
            local_port=8447,
            peer_host="127.0.0.1",
            peer_port=51844,
            peer_server_port=8448,
            type=NodeType.HARVESTER.value,
            n_plots=len(plots),
        )
        dog.farmer_service.connections = [old_harvester]
        old_list = dog.farmer_service.connections

        connection_result = {
            "bytes_read": 732921,
            "bytes_written": 736980,
            "creation_time": 1625781881.464226,
            "last_message_time": 1625856666.3932515,
            "local_port": 8448,
            "node_id": node_id,
            "peer_host": "127.0.0.2",
            "peer_port": 51845,
            "peer_server_port": 8449,
            "type": NodeType.HARVESTER.value,
        }
        harvester_result = {
            "success": True,
            "harvesters": [
                {"plots": plots, "connection": {"node_id": node_id}},
            ],
        }

        MockRpcClient = MockRpcClient.create.return_value
        MockRpcClient.get_connections.return_value = [connection_result]
        MockRpcClient.get_harvesters.return_value = harvester_result
        MockRpcClient.close.return_value = None
        MockRpcClient.await_closed.return_value = None

        # do the thing
        await update_from_farmer(dog)

        # validate
        self.assertTrue(MockRpcClient.get_connections.called)
        self.assertTrue(MockRpcClient.get_harvesters.called)
        self.assertTrue(MockRpcClient.close.called)
        self.assertTrue(MockRpcClient.await_closed.called)

        harvester_list = dog.farmer_service.connections
        self.assertIs(old_list, harvester_list)
        self.assertEqual(len(harvester_list), 1)

        harvester = harvester_list[0]
        for name, value in connection_result.items():
            self.assertEqual(
                value,
                getattr(harvester, name),
                "Harvester attribute '%s' does not match" % name,
            )
        self.assertEqual(harvester.n_plots, len(plots))
