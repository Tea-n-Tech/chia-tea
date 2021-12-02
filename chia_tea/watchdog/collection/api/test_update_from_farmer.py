import sys
import unittest
from unittest import mock

from chia.server.outbound_message import NodeType

from ....models.ChiaWatchdog import ChiaWatchdog
from ....models.FarmerHarvesterAPI import FarmerHarvesterAPI
from ....utils.testing import async_test
from .update_from_farmer import update_from_farmer

# Async testing is hard do in python 3.7 and 3.8 and higher at the same time,
# thus we skip the test in that case.
if sys.version_info >= (3, 8):  # noqa: C901

    class TestUpdateFromFarmer(unittest.TestCase):
        def setUp(self) -> None:
            self.chia_config = {
                "self_hostname": "127.0.0.1",
                "farmer": {"rpc_port": 8008},
            }

        @async_test
        @mock.patch(
            "chia_tea.watchdog.collection.api.update_from_farmer.FarmerRpcClient", autospec=True
        )
        @mock.patch(
            "chia_tea.watchdog.collection.api.update_from_farmer.load_config", autospec=True
        )
        async def test_new_harvester_connected(self, load_config_mock, MockRpcClient):
            dog = ChiaWatchdog("", "")

            node_id = b"1n\x0f\xc4J\xb5q8\xc4\x98\x0b\xe7\\\xac\xd1\x82"
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
                    {"plots": plots, "connection": {"node_id": node_id.hex()}},
                ],
            }

            load_config_mock.return_value = self.chia_config
            MockRpcClient = MockRpcClient.create.return_value
            MockRpcClient.get_connections.return_value = [connection_result]
            MockRpcClient.get_harvesters.return_value = harvester_result
            MockRpcClient.close = mock.MagicMock()
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
        @mock.patch(
            "chia_tea.watchdog.collection.api.update_from_farmer.FarmerRpcClient", autospec=True
        )
        @mock.patch(
            "chia_tea.watchdog.collection.api.update_from_farmer.load_config", autospec=True
        )
        async def test_harvester_disconnected(self, load_config_mock, MockRpcClient):
            dog = ChiaWatchdog("", "")

            node_id = b"1n\x0f\xc4J\xb5q8\xc4\x98\x0b\xe7\\\xac\xd1\x82"
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
            harvester_result = {
                "success": True,
                "harvesters": [],
            }

            load_config_mock.return_value = self.chia_config
            MockRpcClient = MockRpcClient.create.return_value
            MockRpcClient.get_connections.return_value = []
            MockRpcClient.get_harvesters.return_value = harvester_result
            MockRpcClient.close = mock.MagicMock()
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

        @async_test
        @mock.patch(
            "chia_tea.watchdog.collection.api.update_from_farmer.FarmerRpcClient", autospec=True
        )
        @mock.patch(
            "chia_tea.watchdog.collection.api.update_from_farmer.load_config", autospec=True
        )
        async def test_existing_harvester_is_updated(self, load_config_mock, MockRpcClient):
            dog = ChiaWatchdog("", "")

            node_id = b"1n\x0f\xc4J\xb5q8\xc4\x98\x0b\xe7\\\xac\xd1\x82"
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
                    {"plots": plots, "connection": {"node_id": node_id.hex()}},
                ],
            }

            load_config_mock.return_value = self.chia_config
            MockRpcClient = MockRpcClient.create.return_value
            MockRpcClient.get_connections.return_value = [connection_result]
            MockRpcClient.get_harvesters.return_value = harvester_result
            MockRpcClient.close = mock.MagicMock()
            MockRpcClient.await_closed.return_value = None

            # do the thing
            await update_from_farmer(dog)

            # validate
            self.assertTrue(MockRpcClient.get_connections.called)
            self.assertTrue(MockRpcClient.get_harvesters.called)
            self.assertTrue(MockRpcClient.close.called)
            self.assertTrue(MockRpcClient.await_closed.called)
            self.assertTrue(load_config_mock.called)

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
        @mock.patch(
            "chia_tea.watchdog.collection.api.update_from_farmer.FarmerRpcClient", autospec=True
        )
        @mock.patch(
            "chia_tea.watchdog.collection.api.update_from_farmer.load_config", autospec=True
        )
        async def test_harvester_disconnects_between_two_api_calls(
            self, load_config_mock, MockRpcClient
        ):
            # pylint: disable=too-many-locals

            dog = ChiaWatchdog("", "")

            node_id1 = b"1n\x0f\xc4J\xb5q8\xc4\x98\x0b\xe7\\\xac\xd1\x82"
            plots1 = ["only", "length", "is", "used"]
            harvester1 = FarmerHarvesterAPI(
                node_id=node_id1,
                bytes_read=732920,
                bytes_written=736979,
                creation_time=1625781881.0,
                last_message_time=1625856666.0,
                local_port=8447,
                peer_host="127.0.0.1",
                peer_port=51844,
                peer_server_port=8448,
                type=NodeType.HARVESTER.value,
                n_plots=len(plots1),
            )
            node_id2 = b"1n\x0f\xc4J\xb5q8\xc4\x98\x0b\xe7\\\xac\xd1\x81"
            plots2 = ["only", "length", "is", "used", "too"]
            harvester2 = FarmerHarvesterAPI(
                node_id=node_id2,
                bytes_read=732921,
                bytes_written=736980,
                creation_time=1625781882.0,
                last_message_time=1625856667.0,
                local_port=8448,
                peer_host="127.0.0.2",
                peer_port=51845,
                peer_server_port=8449,
                type=NodeType.HARVESTER.value,
                n_plots=len(plots2),
            )
            dog.farmer_service.connections = [harvester1, harvester2]

            connection_result1 = {
                "bytes_read": harvester1.bytes_read,
                "bytes_written": harvester1.bytes_written,
                "creation_time": harvester1.creation_time,
                "last_message_time": harvester1.last_message_time,
                "local_port": harvester1.local_port,
                "node_id": harvester1.node_id,
                "peer_host": harvester1.peer_host,
                "peer_port": harvester1.peer_port,
                "peer_server_port": harvester1.peer_server_port,
                "type": NodeType.HARVESTER.value,
            }
            connection_result2 = {
                "bytes_read": harvester2.bytes_read,
                "bytes_written": harvester2.bytes_written,
                "creation_time": harvester2.creation_time,
                "last_message_time": harvester2.last_message_time,
                "local_port": harvester2.local_port,
                "node_id": harvester2.node_id,
                "peer_host": harvester2.peer_host,
                "peer_port": harvester2.peer_port,
                "peer_server_port": harvester2.peer_server_port,
                "type": NodeType.HARVESTER.value,
            }
            harvester_result = {
                "success": True,
                "harvesters": [
                    {"plots": plots1, "connection": {"node_id": node_id1.hex()}},
                    # harvester 2 is gone
                ],
            }

            load_config_mock.return_value = self.chia_config
            MockRpcClient = MockRpcClient.create.return_value
            MockRpcClient.get_connections.return_value = [connection_result1, connection_result2]
            MockRpcClient.get_harvesters.return_value = harvester_result
            MockRpcClient.close = mock.MagicMock()
            MockRpcClient.await_closed.return_value = None

            # do the thing
            await update_from_farmer(dog)

            # validate
            self.assertTrue(MockRpcClient.get_connections.called)
            self.assertTrue(MockRpcClient.get_harvesters.called)
            self.assertTrue(MockRpcClient.close.called)
            self.assertTrue(MockRpcClient.await_closed.called)
            self.assertTrue(load_config_mock.called)

            harvester_list = dog.farmer_service.connections
            self.assertEqual(len(harvester_list), 1)

            harvester = harvester_list[0]
            for name, value in connection_result1.items():
                self.assertEqual(
                    value,
                    getattr(harvester, name),
                    "Harvester attribute '%s' does not match" % name,
                )
            self.assertEqual(harvester.n_plots, len(plots1))

        @async_test
        @mock.patch(
            "chia_tea.watchdog.collection.api.update_from_farmer.FarmerRpcClient", autospec=True
        )
        @mock.patch(
            "chia_tea.watchdog.collection.api.update_from_farmer.load_config", autospec=True
        )
        async def test_harvester_connects_between_two_api_calls(
            self, load_config_mock, MockRpcClient
        ):
            dog = ChiaWatchdog("", "")

            node_id1 = b"1n\x0f\xc4J\xb5q8\xc4\x98\x0b\xe7\\\xac\xd1\x82"
            plots1 = ["only", "length", "is", "used"]
            harvester1 = FarmerHarvesterAPI(
                node_id=node_id1,
                bytes_read=732920,
                bytes_written=736979,
                creation_time=1625781881.0,
                last_message_time=1625856666.0,
                local_port=8447,
                peer_host="127.0.0.1",
                peer_port=51844,
                peer_server_port=8448,
                type=NodeType.HARVESTER.value,
                n_plots=len(plots1),
            )
            node_id2 = b"1n\x0f\xc4J\xb5q8\xc4\x98\x0b\xe7\\\xac\xd1\x81"
            plots2 = ["only", "length", "is", "used", "too"]
            dog.farmer_service.connections = [harvester1]

            connection_result1 = {
                "bytes_read": harvester1.bytes_read,
                "bytes_written": harvester1.bytes_written,
                "creation_time": harvester1.creation_time,
                "last_message_time": harvester1.last_message_time,
                "local_port": harvester1.local_port,
                "node_id": harvester1.node_id,
                "peer_host": harvester1.peer_host,
                "peer_port": harvester1.peer_port,
                "peer_server_port": harvester1.peer_server_port,
                "type": NodeType.HARVESTER.value,
            }
            harvester_result = {
                "success": True,
                "harvesters": [
                    {"plots": plots1, "connection": {"node_id": node_id1.hex()}},
                    {"plots": plots2, "connection": {"node_id": node_id2.hex()}},
                    # harvester 2 is gone
                ],
            }

            load_config_mock.return_value = self.chia_config
            MockRpcClient = MockRpcClient.create.return_value
            MockRpcClient.get_connections.return_value = [connection_result1]
            MockRpcClient.get_harvesters.return_value = harvester_result
            MockRpcClient.close = mock.MagicMock()
            MockRpcClient.await_closed.return_value = None

            # do the thing
            await update_from_farmer(dog)

            # validate
            self.assertTrue(MockRpcClient.get_connections.called)
            self.assertTrue(MockRpcClient.get_harvesters.called)
            self.assertTrue(MockRpcClient.close.called)
            self.assertTrue(MockRpcClient.await_closed.called)
            self.assertTrue(load_config_mock.called)

            harvester_list = dog.farmer_service.connections
            self.assertEqual(len(harvester_list), 1)

            harvester = harvester_list[0]
            for name, value in connection_result1.items():
                self.assertEqual(
                    value,
                    getattr(harvester, name),
                    "Harvester attribute '%s' does not match" % name,
                )
            self.assertEqual(harvester.n_plots, len(plots1))
