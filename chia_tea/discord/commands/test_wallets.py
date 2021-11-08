import os
import tempfile
import unittest

from google.protobuf.json_format import ParseDict

from ...monitoring.MonitoringDatabase import MonitoringDatabase
from ...protobuf.generated.computer_info_pb2 import ADD, UpdateEvent
from ...protobuf.generated.monitoring_service_pb2 import DataUpdateRequest
from ...utils.testing import async_test
from .wallets import wallets_cmd


class TestWalletsCmd(unittest.TestCase):
    @async_test
    async def test_no_wallets_case(self) -> None:

        with tempfile.TemporaryDirectory() as tmpdir:
            db_filepath = os.path.join(tmpdir, "temp.db")

            with MonitoringDatabase(db_filepath):
                messages = await wallets_cmd(db_filepath)

                self.assertEqual(len(messages), 1)
                self.assertTrue(messages[0].startswith("No wallets"))

    @async_test
    async def test_not_running_wallet_not_displayed(self) -> None:

        with tempfile.TemporaryDirectory() as tmpdir:
            db_filepath = os.path.join(tmpdir, "temp.db")

            with MonitoringDatabase(db_filepath) as db:
                event = ParseDict(
                    js_dict=dict(
                        event_type=ADD,
                        wallet=dict(
                            is_running=False,
                            is_synced=True,
                        ),
                    ),
                    message=UpdateEvent(),
                )
                request = DataUpdateRequest(
                    machine_id=1,
                    machine_name="machine A",
                    timestamp=1000,
                    events=[event],
                )
                db.store_data_update_request(request)

                messages = await wallets_cmd(db_filepath)

                self.assertEqual(len(messages), 1)
                self.assertTrue(messages[0].startswith("No wallets"))

    @async_test
    async def test_display_running_wallet(self) -> None:

        with tempfile.TemporaryDirectory() as tmpdir:
            db_filepath = os.path.join(tmpdir, "tmp.db")

            with MonitoringDatabase(db_filepath) as db:
                update_events = [
                    ParseDict(
                        js_dict=dict(
                            event_type=ADD,
                            wallet=dict(
                                is_running=True,
                                is_synced=True,
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

                messages = await wallets_cmd(db_filepath)
                print(messages)
                # no failure
                self.assertEqual(len(messages), 1)
                msg = messages[0]
                self.assertFalse(msg.startswith("Traceback"))
                # display online harvester
                self.assertTrue("machine A" in msg)
                self.assertIn("synchronized", msg)
