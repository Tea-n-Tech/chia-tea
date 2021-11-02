import os
import tempfile
import unittest

from google.protobuf.json_format import ParseDict

from ...monitoring.MonitoringDatabase import MonitoringDatabase
from ...protobuf.generated.computer_info_pb2 import ADD, UpdateEvent
from ...protobuf.generated.monitoring_service_pb2 import DataUpdateRequest
from ...utils.testing import async_test
from .farmers import farmers_cmd


class TestFarmersCmd(unittest.TestCase):
    @async_test
    async def test_no_farmers_case(self) -> None:

        with tempfile.TemporaryDirectory() as tmpdir:
            db_filepath = os.path.join(tmpdir, "temp.db")

            with MonitoringDatabase(db_filepath):
                messages = await farmers_cmd(db_filepath)

                self.assertEqual(len(messages), 1)
                self.assertTrue(messages[0].startswith("No farmers"))

    @async_test
    async def test_not_running_farmers_not_displayed(self) -> None:

        with tempfile.TemporaryDirectory() as tmpdir:
            db_filepath = os.path.join(tmpdir, "tmp.db")

            with MonitoringDatabase(db_filepath) as db:
                update_event = ParseDict(
                    js_dict=dict(
                        event_type=ADD,
                        farmer=dict(
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

                messages = await farmers_cmd(db_filepath)

                self.assertEqual(len(messages), 1)
                self.assertTrue(messages[0].startswith("No farmers"))

    @async_test
    async def test_farmers_in_db_case(self) -> None:

        with tempfile.TemporaryDirectory() as tmpdir:
            db_filepath = os.path.join(tmpdir, "tmp.db")

            with MonitoringDatabase(db_filepath) as db:
                # machine A has an online farmer with one harvester
                update_events = [
                    ParseDict(
                        js_dict=dict(
                            event_type=ADD,
                            farmer=dict(
                                is_running=True,
                            ),
                        ),
                        message=UpdateEvent(),
                    ),
                    ParseDict(
                        js_dict=dict(
                            event_type=ADD,
                            farmer_harvester=dict(
                                connection_time=500,
                                time_last_msg_received=999,
                                time_last_msg_sent=998,
                                ip_address="1.2.3.4",
                                missed_challenges=1,
                                n_plots=784,
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

                messages = await farmers_cmd(db_filepath)

                # no empty message
                self.assertGreater(len(messages), 1)
                self.assertFalse(messages[0].startswith("No farmers"))
                # display online harvester
                self.assertTrue(any("machine A" in msg for msg in messages))
                self.assertEqual(sum("Harvester" in msg for msg in messages), 1)
                # offline harvesters must not be displayed
                self.assertTrue(all("machine B" not in msg for msg in messages))
