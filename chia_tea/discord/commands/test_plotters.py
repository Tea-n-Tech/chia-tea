import os
import tempfile
import unittest

from google.protobuf.json_format import ParseDict

from ...monitoring.MonitoringDatabase import MonitoringDatabase
from ...protobuf.generated.computer_info_pb2 import ADD, UpdateEvent
from ...protobuf.generated.monitoring_service_pb2 import DataUpdateRequest
from ...utils.testing import async_test
from .plotters import plotters_cmd


class TestPlotterCmd(unittest.TestCase):
    @async_test
    async def test_no_plotter_case(self) -> None:

        with tempfile.TemporaryDirectory() as tmpdir:
            db_filepath = os.path.join(tmpdir, "temp.db")

            with MonitoringDatabase(db_filepath):
                messages = await plotters_cmd(db_filepath)

                self.assertEqual(len(messages), 1)
                self.assertTrue(messages[0].startswith("No Plotters"))

    @async_test
    async def test_display_monitored_plotter(self) -> None:

        with tempfile.TemporaryDirectory() as tmpdir:
            db_filepath = os.path.join(tmpdir, "tmp.db")

            with MonitoringDatabase(db_filepath) as db:
                update_events = [
                    ParseDict(
                        js_dict=dict(
                            event_type=ADD,
                            plotting_plot=dict(
                                id="id",
                                pool_public_key="pool_public_key",
                                start_time=999.0,
                                progress=0.1,
                                state="Some Phase",
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

                messages = await plotters_cmd(db_filepath)
                # no failure
                self.assertEqual(len(messages), 3)
                title_msg = messages[0]
                msg = messages[2]
                self.assertFalse(title_msg.startswith("No Plotters"))
                self.assertFalse(title_msg.startswith("Traceback"))
                # display online harvester
                self.assertIn("Plotters", title_msg)
                self.assertIn("Plot id", msg)
                self.assertIn("Since:", msg)
                self.assertIn("State: Some Phase", msg)
                self.assertIn("Progress: 10.0%", msg)
