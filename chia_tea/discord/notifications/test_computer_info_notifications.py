import unittest

from google.protobuf.json_format import ParseDict

from ...protobuf.generated.chia_pb2 import HarvesterViewedFromFarmer
from ...protobuf.generated.computer_info_pb2 import ComputerInfo
from ...protobuf.generated.machine_info_pb2 import MachineInfo
from .computer_info_notifications import (
    HARVESTER_TIMOUT, get_msg_if_farmer_harvester_timed_out,
    notify_on_harvester_reward_found, notify_on_wallet_connection_change,
    notify_on_wallet_sync_change)


class TestComputerInfoNotifications(unittest.TestCase):

    def test_farmer_harvester_reward_found_notification(self):

        machine = MachineInfo()

        old_computer_info = ParseDict(
            js_dict={
                "harvester": {"n_proofs": 0}
            },
            message=ComputerInfo(),
        )
        new_computer_info = ParseDict(
            js_dict={
                "harvester": {"n_proofs": 1}
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
                "harvester": {"n_proofs": 1}
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
                "harvester": {"n_proofs": 0}
            },
            message=ComputerInfo(),
        )
        new_computer_info = ParseDict(
            js_dict={
                "harvester": {"n_proofs": 0}
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
                "wallet": {"is_synced": True}
            },
            message=ComputerInfo(),
        )
        new_computer_info = ParseDict(
            js_dict={
                "wallet": {"is_synced": False}
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
                "wallet": {"is_synced": False}
            },
            message=ComputerInfo(),
        )
        new_computer_info = ParseDict(
            js_dict={
                "wallet": {"is_synced": True}
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
                "wallet": {"is_running": False}
            },
            message=ComputerInfo(),
        )
        new_computer_info = ParseDict(
            js_dict={
                "wallet": {"is_running": True}
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
                "wallet": {"is_running": True}
            },
            message=ComputerInfo(),
        )
        new_computer_info = ParseDict(
            js_dict={
                "wallet": {"is_running": False}
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

        # we dont perform a unittest on the notifier itself
        # since it's timing logic is hard to test. Instead
        # we test the internal wrapper function.

        # no msg case if all is good
        barely_ok_farmer_harvester = ParseDict(
            js_dict={"time_last_msg_received": 1},
            message=HarvesterViewedFromFarmer(),
        )
        msg = get_msg_if_farmer_harvester_timed_out(
            harvester=barely_ok_farmer_harvester,
            last_timestamp=59,
            new_timestamp=60,
            machine=machine,
        )
        self.assertTrue(msg == "")

        # on startup no message is given if a harvester
        # is already timed out to avoid spamming the chat
        # on restarts of the bot.
        msg_timestamp = 1
        timed_out_farmer_harvester = ParseDict(
            js_dict={"time_last_msg_received": msg_timestamp},
            message=HarvesterViewedFromFarmer(),
        )
        msg = get_msg_if_farmer_harvester_timed_out(
            harvester=timed_out_farmer_harvester,
            last_timestamp=0,
            new_timestamp=msg_timestamp+HARVESTER_TIMOUT+2,
            machine=machine,
        )
        self.assertTrue(msg == "")

        # test general timeout notification mechanism
        msg = get_msg_if_farmer_harvester_timed_out(
            harvester=timed_out_farmer_harvester,
            last_timestamp=msg_timestamp+HARVESTER_TIMOUT-1,
            new_timestamp=msg_timestamp+HARVESTER_TIMOUT,
            machine=machine,
        )
        self.assertTrue(len(msg) != 0)
