
import unittest

from google.protobuf.json_format import ParseDict

from ...monitoring.MonitoringDatabase import MonitoringDatabase
from ..generated.computer_info_pb2 import ADD, DELETE, UPDATE, UpdateEvent
from .sql_cmds import get_update_events_from_db, insert_update_event_in_db


class TestSqlCmds(unittest.TestCase):

    def test_that_fetched_events_have_correct_event_type(self):

        event_types_to_test = [
            ADD,
            UPDATE,
            DELETE
        ]

        db = MonitoringDatabase(":memory:")
        with db:
            update_event = ParseDict(
                js_dict=dict(
                    event_type=ADD,
                    farmer_harvester=dict(
                        id='some plot id 1',
                    )
                ),
                message=UpdateEvent()
            )
            for i_event, event_type in enumerate(event_types_to_test):
                update_event.event_type = event_type
                insert_update_event_in_db(
                    sql_cursor=db.cursor,
                    pb_message=update_event,
                    meta_attributes={
                        "machine_id": 1,
                        'timestamp': i_event,
                        "event_type": update_event.event_type,
                    }
                )

            machine_events = get_update_events_from_db(
                db.cursor,
                # timestamps inbetween which to fetch data
                0,
                len(event_types_to_test)
            )

            self.assertEqual(len(machine_events), 1)
            machine_id, event_list = next(iter(machine_events.items()))
            self.assertEqual(machine_id, 1)
            self.assertEqual(len(event_list), 3)
            for event, desired_event_type in zip(event_list, event_types_to_test):
                self.assertEqual(event.event_type, desired_event_type)
