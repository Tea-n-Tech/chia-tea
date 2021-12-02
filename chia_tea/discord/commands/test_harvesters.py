import os
import tempfile
import unittest

from google.protobuf.json_format import ParseDict

from ...monitoring.MonitoringDatabase import MonitoringDatabase
from ...protobuf.generated.computer_info_pb2 import ADD, UpdateEvent
from ...protobuf.generated.monitoring_service_pb2 import DataUpdateRequest
from ...utils.testing import async_test
from .harvesters import harvesters_cmd


class TestHarvestersCmd(unittest.TestCase):
    @async_test
    async def test_no_harvesters_case(self) -> None:

        with tempfile.TemporaryDirectory() as tmpdir:
            db_filepath = os.path.join(tmpdir, "temp.db")

            with MonitoringDatabase(db_filepath):
                messages = await harvesters_cmd(db_filepath)

                self.assertEqual(len(messages), 1)
                self.assertTrue(messages[0].startswith("No Harvesters"))

    @async_test
    async def test_not_running_harvester_not_displayed(self) -> None:

        with tempfile.TemporaryDirectory() as tmpdir:
            db_filepath = os.path.join(tmpdir, "tmp.db")

            with MonitoringDatabase(db_filepath) as db:
                update_event = ParseDict(
                    js_dict=dict(
                        event_type=ADD,
                        harvester=dict(
                            is_running=False,
                        ),
                    ),
                    message=UpdateEvent(),
                )
                request = DataUpdateRequest(
                    machine_id=2,
                    machine_name="machine B",
                    timestamp=1000,
                    events=[update_event],
                )
                db.store_data_update_request(request)

                messages = await harvesters_cmd(db_filepath)

                self.assertEqual(len(messages), 1)
                self.assertTrue(messages[0].startswith("No Harvesters"))
                self.assertTrue("machine B" not in messages[0])

    @async_test
    async def test_harvesters_in_db_case(self) -> None:

        with tempfile.TemporaryDirectory() as tmpdir:
            db_filepath = os.path.join(tmpdir, "tmp.db")

            with MonitoringDatabase(db_filepath) as db:
                # machine A:
                # - Harvester (running)
                # - 1 Disk
                # - 1 Plot
                update_events = [
                    ParseDict(
                        js_dict=dict(
                            event_type=ADD,
                            harvester=dict(
                                is_running=True,
                                n_proofs=1,
                            ),
                        ),
                        message=UpdateEvent(),
                    ),
                    ParseDict(
                        js_dict=dict(
                            event_type=ADD,
                            harvester_plot=dict(
                                id="plot1",
                                filename="/path/to/plot1",
                                filesize=1e8,
                                pool_contract_puzzle_hash="pool_contract_puzzle_hash",
                                pool_public_key="pool_public_key",
                                size=32,
                                time_modified=10,
                            ),
                        ),
                        message=UpdateEvent(),
                    ),
                    ParseDict(
                        js_dict=dict(
                            event_type=ADD,
                            harvester_plot=dict(
                                id="plot1",
                                filename="/path/to/plot1",
                                filesize=1e8,
                                pool_contract_puzzle_hash="pool_contract_puzzle_hash",
                                pool_public_key="pool_public_key",
                                size=32,
                                time_modified=10,
                            ),
                        ),
                        message=UpdateEvent(),
                    ),
                    ParseDict(
                        js_dict=dict(
                            event_type=ADD,
                            disk=dict(
                                id="disk1",
                                name="some disk",
                                total_space=2e8,
                                used_space=1e8,
                                device="some device",
                                mountpoint="/mnt/plots",
                                fstype="ext4",
                                mount_options="ro",
                            ),
                        ),
                        message=UpdateEvent(),
                    ),
                ]
                request = DataUpdateRequest(
                    machine_id=1,
                    machine_name="machine A",
                    timestamp=1000,
                    events=update_events,
                )
                db.store_data_update_request(request)

                messages = await harvesters_cmd(db_filepath)

                # no failure
                self.assertEqual(len(messages), 1)
                msg = messages[0]
                self.assertFalse(msg.startswith("Traceback"))
                # display online harvester
                self.assertTrue("machine A" in msg)
                self.assertEqual(msg.count("🚜 Harvester"), 1)
                self.assertEqual(msg.count("disk1"), 1)
                self.assertEqual(msg.count("plots: 1"), 1)
                self.assertEqual(msg.count("proofs: 1"), 1)
