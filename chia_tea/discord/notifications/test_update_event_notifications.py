import unittest

from google.protobuf.json_format import ParseDict

from ...protobuf.generated.computer_info_pb2 import (ADD, DELETE, UPDATE,
                                                     UpdateEvent)
from .update_event_notifications import (
    notify_if_a_disk_is_lost, notify_if_plots_are_lost, notify_on_full_ram,
    notify_when_farmer_connects_or_disconnects_to_harvester)


class TestUpdateEventNotifications(unittest.TestCase):

    def test_msg_if_farmer_connects_to_harvesters(self):

        update_event = ParseDict(
            js_dict=dict(
                event_type=ADD,
                farmer_harvester=dict(
                    id="harvester id",
                    ip_address="some ip",
                )
            ),
            message=UpdateEvent())

        messages = notify_when_farmer_connects_or_disconnects_to_harvester(
            machine_id="some machine id",
            update_events=[update_event]
        )

        self.assertEqual(len(messages), 1)

    def test_msg_if_farmer_disconnects_to_harvesters(self):

        update_event = ParseDict(
            js_dict=dict(
                event_type=DELETE,
                farmer_harvester=dict(
                    id="harvester id",
                    ip_address="some ip",
                )
            ),
            message=UpdateEvent())

        messages = notify_when_farmer_connects_or_disconnects_to_harvester(
            machine_id="some machine id",
            update_events=[update_event]
        )

        self.assertEqual(len(messages), 1)

    def test_no_msg_if_farmer_to_harvesters_status_just_updates(self):

        update_event = ParseDict(
            js_dict=dict(
                event_type=UPDATE,
                farmer_harvester=dict(
                    id="harvester id",
                    ip_address="some ip",
                )
            ),
            message=UpdateEvent())

        messages = notify_when_farmer_connects_or_disconnects_to_harvester(
            machine_id="some machine id",
            update_events=[update_event]
        )

        self.assertEqual(len(messages), 0)

    def test_msg_if_ram_full(self):

        update_event = ParseDict(
            js_dict=dict(
                ram=dict(
                    total_ram=100,
                    used_ram=96,
                )
            ),
            message=UpdateEvent())

        messages = notify_on_full_ram(
            machine_id="some machine id",
            update_events=[update_event],
        )

        self.assertEqual(len(messages), 1)

    def test_no_msg_if_ram_ok(self):

        update_event = ParseDict(
            js_dict=dict(
                ram=dict(
                    total_ram=100,
                    used_ram=80,
                )
            ),
            message=UpdateEvent()
        )

        messages = notify_on_full_ram(
            machine_id="some machine id",
            update_events=[update_event],
        )

        self.assertEqual(len(messages), 0)

    def test_msg_if_disk_is_lost(self):

        update_event = ParseDict(
            js_dict=dict(
                event_type=DELETE,
                disk=dict(
                    name='/somedir',
                )
            ),
            message=UpdateEvent()
        )

        messages = notify_if_a_disk_is_lost(
            "some machine id",
            update_events=[update_event]
        )
        self.assertEqual(len(messages), 1)

    def test_no_msg_if_disk_is_added_or_updated(self):

        update_event = ParseDict(
            js_dict=dict(
                event_type=ADD,
                disk=dict(
                    name='/somedir',
                )
            ),
            message=UpdateEvent()
        )

        messages = notify_if_a_disk_is_lost(
            "some machine id",
            update_events=[update_event]
        )
        self.assertEqual(len(messages), 0)

        update_event.event_type = UPDATE
        messages = notify_if_a_disk_is_lost(
            "some machine id",
            update_events=[update_event]
        )
        self.assertEqual(len(messages), 0)

    def test_msg_if_plots_are_lost(self):

        update_event = ParseDict(
            js_dict=dict(
                event_type=DELETE,
                harvester_plot=dict(
                    id='some plot id 1',
                )
            ),
            message=UpdateEvent()
        )

        messages = notify_if_plots_are_lost(
            "some machine id",
            update_events=[update_event]
        )
        self.assertEqual(len(messages), 1)
        self.assertTrue("1" in messages[0])

    def test_no_msg_if_plot_is_added_or_updated(self):

        update_event = ParseDict(
            js_dict=dict(
                event_type=ADD,
                harvester_plot=dict(
                    id='some plot id 1',
                )
            ),
            message=UpdateEvent()
        )

        messages = notify_if_plots_are_lost(
            "some machine id",
            update_events=[update_event]
        )
        self.assertEqual(len(messages), 0)

        update_event.event_type = UPDATE
        messages = notify_if_plots_are_lost(
            "some machine id",
            update_events=[update_event]
        )
        self.assertEqual(len(messages), 0)
