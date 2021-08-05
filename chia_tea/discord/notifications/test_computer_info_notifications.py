import unittest

from google.protobuf.json_format import ParseDict

from ...protobuf.generated.computer_info_pb2 import ComputerInfo
from ...protobuf.generated.machine_info_pb2 import MachineInfo
from .computer_info_notifications import (notify_on_harvester_reward_found,
                                          notify_on_wallet_connection_change,
                                          notify_on_wallet_sync_change, notify_when_harvester_times_out)


class TestComputerInfoNotifications(unittest.TestCase):

    def test_farmer_harvester_reward_found_notification(self):

        machine = MachineInfo()

        old_computer_info = ParseDict(
            js_dict={
                "harvester_info": {"n_proofs": 0}
            },
            message=ComputerInfo(),
        )
        new_computer_info = ParseDict(
            js_dict={
                "harvester_info": {"n_proofs": 1}
            },
            message=ComputerInfo(),
        )

        messages = notify_on_harvester_reward_found(
            machine,
            old_computer_info=old_computer_info,
            new_computer_info=new_computer_info,
        )

        self.assertEqual(len(messages), 1)

    def test_farmer_harvester_newly_registered_and_reward_found(self):

        machine = MachineInfo()

        old_computer_info = ParseDict(
            js_dict={},
            message=ComputerInfo(),
        )
        new_computer_info = ParseDict(
            js_dict={
                "harvester_info": {"n_proofs": 1}
            },
            message=ComputerInfo(),
        )

        messages = notify_on_harvester_reward_found(
            machine,
            old_computer_info=old_computer_info,
            new_computer_info=new_computer_info,
        )

        self.assertEqual(len(messages), 1)

    def test_farmer_harvester_no_reward_found_notification(self):

        machine = MachineInfo()

        old_computer_info = ParseDict(
            js_dict={
                "harvester_info": {"n_proofs": 0}
            },
            message=ComputerInfo(),
        )
        new_computer_info = ParseDict(
            js_dict={
                "harvester_info": {"n_proofs": 0}
            },
            message=ComputerInfo(),
        )

        messages = notify_on_harvester_reward_found(
            machine,
            old_computer_info=old_computer_info,
            new_computer_info=new_computer_info,
        )

        self.assertEqual(len(messages), 0)

    def test_msg_if_wallet_not_synced_anymore(self):

        machine = MachineInfo()

        old_computer_info = ParseDict(
            js_dict={
                "wallet_info": {"is_synced": True}
            },
            message=ComputerInfo(),
        )
        new_computer_info = ParseDict(
            js_dict={
                "wallet_info": {"is_synced": False}
            },
            message=ComputerInfo(),
        )

        messages = notify_on_wallet_sync_change(
            machine=machine,
            old_computer_info=old_computer_info,
            new_computer_info=new_computer_info,
        )

        self.assertEqual(len(messages), 1)

    def test_msg_if_wallet_not_synced_again(self):

        machine = MachineInfo()

        old_computer_info = ParseDict(
            js_dict={
                "wallet_info": {"is_synced": False}
            },
            message=ComputerInfo(),
        )
        new_computer_info = ParseDict(
            js_dict={
                "wallet_info": {"is_synced": True}
            },
            message=ComputerInfo(),
        )

        messages = notify_on_wallet_sync_change(
            machine=machine,
            old_computer_info=old_computer_info,
            new_computer_info=new_computer_info,
        )

        self.assertEqual(len(messages), 1)

    def test_msg_if_wallet_has_started(self):

        machine = MachineInfo()

        old_computer_info = ParseDict(
            js_dict={
                "wallet_info": {"is_running": False}
            },
            message=ComputerInfo(),
        )
        new_computer_info = ParseDict(
            js_dict={
                "wallet_info": {"is_running": True}
            },
            message=ComputerInfo(),
        )

        messages = notify_on_wallet_connection_change(
            machine=machine,
            old_computer_info=old_computer_info,
            new_computer_info=new_computer_info,
        )

        self.assertEqual(len(messages), 1)

    def test_msg_if_wallet_has_stopped(self):

        machine = MachineInfo()

        old_computer_info = ParseDict(
            js_dict={
                "wallet_info": {"is_running": True}
            },
            message=ComputerInfo(),
        )
        new_computer_info = ParseDict(
            js_dict={
                "wallet_info": {"is_running": False}
            },
            message=ComputerInfo(),
        )

        messages = notify_on_wallet_connection_change(
            machine=machine,
            old_computer_info=old_computer_info,
            new_computer_info=new_computer_info,
        )

        self.assertEqual(len(messages), 1)

    def test_notification_on_timeout(self):

        machine = MachineInfo()

        old_computer_info = ParseDict(
            js_dict={
                "connected_harvesters": [{"n_timeouts": 0}]
            },
            message=ComputerInfo(),
        )
        new_computer_info = ParseDict(
            js_dict={
                "connected_harvesters": [{"n_timeouts": 1}]
            },
            message=ComputerInfo(),
        )
        messages = notify_when_harvester_times_out(
            machine,
            old_computer_info=old_computer_info,
            new_computer_info=new_computer_info,
        )
        self.assertEqual(len(messages), 1)

        # no message test
        messages = notify_when_harvester_times_out(
            machine,
            old_computer_info=old_computer_info,
            new_computer_info=old_computer_info,
        )
        self.assertEqual(len(messages), 0)
