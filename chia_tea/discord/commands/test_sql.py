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

            with MonitoringDatabase(db_filepath) as db:

                update_events = [
                    ParseDict(
                        js_dict=dict(
                            event_type=ADD,
                            cpu=dict(
                                usage=0.1,
                            )
                        ),
                        message=UpdateEvent()
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
                    db_filepath, [
                        # empty command (returns nothing)
                        "",
                        # error command
                        "ERROR ~!!#*)!(*#;",
                        # create table is not allowed (read only)
                        "CREATE TABLE yay (pewpew text)",
                        # valid sql command
                        "SELECT * FROM CPU",
                    ])

                self.assertEqual(len(messages), 3)
                self.assertTrue("syntax error" in messages[0])
                self.assertEqual(
                    "attempt to write a readonly database", messages[1])
                self.assertTrue(
                    "usage" in messages[2] and "0.1" in messages[2])
