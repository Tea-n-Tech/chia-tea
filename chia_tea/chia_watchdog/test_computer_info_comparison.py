
import unittest

from ..protobuf.generated.chia_pb2 import HarvesterPlot
from ..protobuf.generated.computer_info_pb2 import (_COMPUTERINFO, ADD, DELETE,
                                                    UPDATE, ComputerInfo,
                                                    UpdateEvent)
from ..protobuf.generated.hardware_pb2 import Cpu
from ..utils.testing import async_test
from .computer_info_comparison import compare_computer_info


class TestMonitoringClient(unittest.TestCase):

    @async_test
    async def test_compare_empty_computer_info(self):

        old_computer_info = ComputerInfo()
        new_computer_info = ComputerInfo()
        events = [
            event
            async for event in compare_computer_info(
                old_computer_info,
                new_computer_info
            )
        ]
        self.assertListEqual(list(events), [])

    @async_test
    async def test_compare_computer_info_update_non_iterable(self):

        event_data = Cpu(name="my_cpu")

        old_computer_info = ComputerInfo()
        new_computer_info = ComputerInfo(
            cpu=event_data
        )
        events = [
            event
            async for event in compare_computer_info(
                old_computer_info,
                new_computer_info
            )
        ]
        expected = [
            UpdateEvent(
                event_type=UPDATE,
                cpu=event_data,
            )]

        self.assertListEqual(list(events), expected)

    @async_test
    async def test_compare_computer_info_iterables(self):

        old_computer_info = ComputerInfo(
            harvester_plots=[
                HarvesterPlot(
                    id="remove me"
                ),
                HarvesterPlot(
                    id="changed"
                ),
                HarvesterPlot(
                    id="nothing"
                )
            ]
        )
        new_computer_info = ComputerInfo(
            harvester_plots=[
                HarvesterPlot(
                    id="add me",
                ),
                HarvesterPlot(
                    id="changed",
                    filename="something changed"
                ),
                HarvesterPlot(
                    id="nothing"
                )
            ]
        )
        events = [
            event
            async for event in compare_computer_info(
                old_computer_info,
                new_computer_info
            )
        ]
        expected = [
            UpdateEvent(
                event_type=ADD,
                harvester_plot=HarvesterPlot(
                    id="add me",
                )
            ),
            UpdateEvent(
                event_type=UPDATE,
                harvester_plot=HarvesterPlot(
                    id="changed",
                    filename="something changed"
                )
            ),
            UpdateEvent(
                event_type=DELETE,
                harvester_plot=HarvesterPlot(
                    id="remove me",
                )
            ),
        ]

        self.assertListEqual(list(events), expected)

    def test_update_event_and_computer_info_have_matching_fields(self):

        computer_info_field_types = [
            field.message_type for field in _COMPUTERINFO.fields
            if field.name not in ("timestamp", "machine_id")
        ]
        update_event_type = [
            field.message_type for field in _COMPUTERINFO.fields
            if field.name != "event_type"
        ]

        for field_type1 in computer_info_field_types:
            self.assertIn(field_type1, update_event_type)
        # self.assertListEqual(computer_info_field_types, update_event_type)
