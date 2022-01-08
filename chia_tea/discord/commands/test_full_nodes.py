import os
import tempfile
import unittest
from datetime import datetime

from google.protobuf.json_format import ParseDict

from ...monitoring.MonitoringDatabase import MonitoringDatabase
from ...protobuf.generated.computer_info_pb2 import ADD, UpdateEvent
from ...protobuf.generated.monitoring_service_pb2 import DataUpdateRequest
from ...utils.testing import async_test
from .full_nodes import full_nodes_cmd


class TestFullNodeCmd(unittest.TestCase):
    @async_test
    async def test_no_full_nodes_case(self) -> None:

        with tempfile.TemporaryDirectory() as tmpdir:
            db_filepath = os.path.join(tmpdir, "temp.db")

            with MonitoringDatabase(db_filepath):
                messages = await full_nodes_cmd(db_filepath)

                self.assertEqual(len(messages), 1)
                self.assertTrue(messages[0].startswith("No Full Nodes"))

    @async_test
    async def test_not_running_full_nodes_not_displayed(self) -> None:

        with tempfile.TemporaryDirectory() as tmpdir:
            db_filepath = os.path.join(tmpdir, "temp.db")
            now_timestamp = datetime.now().timestamp()

            with MonitoringDatabase(db_filepath) as db:
                event = ParseDict(
                    js_dict=dict(
                        event_type=ADD,
                        full_node=dict(
                            is_running=False,
                            is_synced=True,
                            sync_blockchain_height=0,
                            sync_node_height=0,
                        ),
                    ),
                    message=UpdateEvent(),
                )
                request = DataUpdateRequest(
                    machine_id=1,
                    machine_name="machine A",
                    timestamp=now_timestamp,
                    events=[event],
                )
                db.store_data_update_request(request)

                messages = await full_nodes_cmd(db_filepath)

                self.assertEqual(len(messages), 1)
                self.assertTrue(messages[0].startswith("No Full Nodes"))

    @async_test
    async def test_display_running_full_nodes(self) -> None:

        with tempfile.TemporaryDirectory() as tmpdir:
            db_filepath = os.path.join(tmpdir, "tmp.db")
            now_timestamp = datetime.now().timestamp()

            with MonitoringDatabase(db_filepath) as db:
                update_events = [
                    ParseDict(
                        js_dict=dict(
                            event_type=ADD,
                            full_node=dict(
                                is_running=True,
                                is_synced=True,
                                # setting this to zero tests for a zero
                                # division bug
                                sync_blockchain_height=0,
                                sync_node_height=0,
                            ),
                        ),
                        message=UpdateEvent(),
                    ),
                ]
                request = DataUpdateRequest(
                    machine_id=1,
                    machine_name="machine A",
                    timestamp=now_timestamp,
                    events=update_events,
                )
                db.store_data_update_request(request)

                messages = await full_nodes_cmd(db_filepath)

                self.assertEqual(len(messages), 1)
                msg = messages[0]
                self.assertFalse(msg.startswith("Traceback"))
                self.assertIn("synchronized", msg)
