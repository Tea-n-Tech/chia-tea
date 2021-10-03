import os
import tempfile
import unittest

from google.protobuf.json_format import ParseDict

from ...monitoring.MonitoringDatabase import MonitoringDatabase
from ...protobuf.generated.computer_info_pb2 import ADD, UpdateEvent
from ...protobuf.generated.monitoring_service_pb2 import DataUpdateRequest
from ...utils.testing import async_test
from .sql import sql_cmd


class TestSqlCmd(unittest.TestCase):
    @async_test
    async def test_syntax_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_filepath = os.path.join(tmpdir, "temp.db")
            with MonitoringDatabase(db_filepath):
                messages = await sql_cmd(db_filepath, "ERROR ~!!#*)!(*#;")

                self.assertEqual(len(messages), 1)
                self.assertIn("syntax error", messages[0])

    @async_test
    async def test_empty_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_filepath = os.path.join(tmpdir, "temp.db")
            with MonitoringDatabase(db_filepath):
                messages = await sql_cmd(
                    db_filepath,
                    "",
                )
                self.assertEqual(len(messages), 1)
                self.assertIn("No entries found", messages[0])

    @async_test
    async def test_if_readonly_protected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_filepath = os.path.join(tmpdir, "temp.db")
            with MonitoringDatabase(db_filepath):
                messages = await sql_cmd(
                    db_filepath,
                    "CREATE TABLE yay (pewpew text)",
                )
                self.assertEqual(len(messages), 1)
                self.assertEqual("attempt to write a readonly database", messages[0])

    @async_test
    async def test_valid_select_cmd(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_filepath = os.path.join(tmpdir, "temp.db")
            with MonitoringDatabase(db_filepath) as db:
                update_events = [
                    ParseDict(
                        js_dict=dict(
                            event_type=ADD,
                            cpu=dict(
                                usage=0.1,
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

                messages = await sql_cmd(
                    db_filepath,
                    "SELECT * FROM CPU",
                )
                self.assertEqual(len(messages), 1)
                self.assertIn("usage", messages[0])
                self.assertIn("0.1", messages[0])
