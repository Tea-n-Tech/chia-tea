import unittest
from datetime import datetime

from ..ChiaWatchdog import ChiaWatchdog
from .FarmerHarvesterLogfile import FarmerHarvesterLogfile
from .line_checks import (ActionHarvesterConnected,
                          ActionHarvesterDisconnected,
                          ActionHarvesterFoundProof,
                          ActionMessageFromHarvester,
                          ActionFinishedSignagePoint,
                          ActionMessageToHarvester)

# pylint: skip-file


class TestLineAction(unittest.TestCase):

    def test_harvester_disconnected(self):

        action = ActionHarvesterDisconnected()

        node_id = "d46fb9aaaa01f3aa3fc04f3e43231d35c3a1ddd4"
        ip_address = "57.22.39.97"
        timestamp_str = "2021-05-26T09:37:13.872"
        timestamp = datetime.fromisoformat(timestamp_str)

        line = (
            f"{timestamp_str} farmer farmer_server              : INFO"
            + f"     Connection closed: {ip_address},"
            + f" node id: {node_id}"
        )

        self.assertTrue(action.is_match(line))

        # check case that harvester does not exist yet
        chia_dog = ChiaWatchdog("")

        action.apply(line, chia_dog)
        self.assertTrue(len(chia_dog.harvester_infos) == 1)
        harvester_info = list(chia_dog.harvester_infos.values())[0]
        self.assertEqual(
            harvester_info.ip_address,
            ip_address
        )
        self.assertEqual(
            harvester_info.harvester_id,
            node_id
        )
        self.assertEqual(harvester_info.is_connected, False)
        self.assertEqual(
            harvester_info.last_update,
            timestamp
        )

        # check in case harvester exists
        chia_dog.harvester_infos = {
            node_id: FarmerHarvesterLogfile(
                node_id,
                ip_address,
                timestamp,
                True,
            )
        }
        action.apply(line, chia_dog)
        self.assertTrue(len(chia_dog.harvester_infos) == 1)
        harvester_info = list(chia_dog.harvester_infos.values())[0]
        self.assertEqual(
            harvester_info.ip_address,
            ip_address
        )
        self.assertEqual(
            harvester_info.harvester_id,
            node_id
        )
        self.assertEqual(harvester_info.is_connected, False)
        self.assertEqual(
            harvester_info.last_update,
            timestamp
        )

    def test_harvester_connected(self):

        action = ActionHarvesterConnected()

        node_id = "d46fb9aaaa01f3aa3fc04f3e43231d35c3a1ddd4"
        ip_address = "57.22.39.97"
        timestamp_str = "2021-05-26T09:37:13.872"
        timestamp = datetime.fromisoformat(timestamp_str)

        line = (
            f"{timestamp_str} farmer farmer_server           " +
            f"   : DEBUG    -> harvester_handshake to peer {ip_address} " +
            node_id)

        self.assertTrue(action.is_match(line))

        # check case that harvester does not exist yet
        chia_dog = ChiaWatchdog("")

        action.apply(line, chia_dog)
        self.assertTrue(len(chia_dog.harvester_infos) == 1)
        harvester_info = list(chia_dog.harvester_infos.values())[0]
        self.assertEqual(
            harvester_info.ip_address,
            ip_address
        )
        self.assertEqual(
            harvester_info.harvester_id,
            node_id
        )
        self.assertEqual(harvester_info.is_connected, True)
        self.assertEqual(
            harvester_info.last_update,
            timestamp
        )

        # check in case harvester exists
        chia_dog.harvester_infos = {
            node_id: FarmerHarvesterLogfile(
                node_id,
                ip_address,
                timestamp,
                True,
            )
        }
        action.apply(line, chia_dog)
        self.assertTrue(len(chia_dog.harvester_infos) == 1)
        harvester_info = list(chia_dog.harvester_infos.values())[0]
        self.assertEqual(
            harvester_info.ip_address,
            ip_address
        )
        self.assertEqual(
            harvester_info.harvester_id,
            node_id
        )
        self.assertEqual(harvester_info.is_connected, True)
        self.assertEqual(
            harvester_info.last_update,
            timestamp
        )

    def test_farmer_message_to_harvester(self):

        action = ActionMessageToHarvester()

        node_id = "d46fb9aaaa01f3aa3fc04f3e43231d35c3a1ddd4"
        ip_address = "57.22.39.97"
        timestamp_str = "2021-05-26T09:37:13.872"

        line = msg_to_harvester(timestamp_str, ip_address, node_id)
        # check line detection
        self.assertTrue(action.is_match(line))

        # check correct modification
        chia_dog = ChiaWatchdog("")
        action.apply(line, chia_dog)

        self.assertEqual(len(chia_dog.harvester_infos), 1)
        harvester = chia_dog.harvester_infos[node_id]
        self.assertEqual(harvester.ip_address, ip_address)
        self.assertEqual(harvester.harvester_id, node_id)
        self.assertEqual(harvester.is_connected, False)

    def test_farmer_message_from_harvester(self):

        action = ActionMessageFromHarvester()

        node_id = "d46fb9aaaa01f3aa3fc04f3e43231d35c3a1ddd4"
        ip_address = "57.22.39.97"
        timestamp_str = "2021-05-26T09:37:13.872"

        line = msg_from_harvester(timestamp_str, ip_address, node_id)

        # check line detection
        self.assertTrue(action.is_match(line))

        # check correct modification
        chia_dog = ChiaWatchdog("")
        action.apply(line, chia_dog)

        self.assertEqual(len(chia_dog.harvester_infos), 1)
        harvester = chia_dog.harvester_infos[node_id]
        self.assertEqual(harvester.ip_address, ip_address)
        self.assertEqual(harvester.harvester_id, node_id)
        self.assertEqual(harvester.is_connected, True)

    def test_harvester_found_proof(self):
        action1 = ActionHarvesterFoundProof()

        line = (
            "2021-06-16T22:44:56.890 " +
            "harvester chia.harvester.harvester: " +
            "INFO 0 plots were eligible for farming 65322a31ad... " +
            "Found 0 proofs. Time: 0.00015 s. Total 0 plots"
        )
        line1Found = (
            "2021-06-16T22:44:56.890 " +
            "harvester chia.harvester.harvester: " +
            "INFO 0 plots were eligible for farming 65322a31ad... " +
            "Found 1 proofs. Time: 0.00015 s. Total 0 plots"
        )
        line10Found = (
            "2021-06-16T22:44:56.890 " +
            "harvester chia.harvester.harvester: " +
            "INFO 0 plots were eligible for farming 65322a31ad... " +
            "Found 10 proofs. Time: 0.00015 s. Total 0 plots"
        )

        self.assertTrue(action1.is_match(line))
        self.assertTrue(action1.is_match(line1Found))
        self.assertTrue(action1.is_match(line10Found))

        chia_dog = ChiaWatchdog("")

        action1.apply(line, chia_dog)
        harvester_service = chia_dog.harvester_service
        self.assertEqual(harvester_service.n_proofs, 0)
        action1.apply(line1Found, chia_dog)
        self.assertEqual(harvester_service.n_proofs, 1)
        action1.apply(line10Found, chia_dog)
        self.assertEqual(harvester_service.n_proofs, 11)

    def test_harvester_msgs_timouts(self):
        """
        This test is done for the new logic with sgn points
        """
        # pylint: disable=too-many-locals

        chia_dog = ChiaWatchdog("")

        node_id = "d46fb9aaaa01f3aa3fc04f3e43231d35c3a1ddd4"
        ip_address = "57.22.39.97"

        timestamp0_str = "2021-05-26T09:30:00.872"  # signage - should not fail
        timestamp1_str = "2021-05-26T09:30:01.872"  # send
        timestamp2_str = "2021-05-26T09:30:02.872"  # recieve
        timestamp3_str = "2021-05-26T09:30:20.872"  # signage - not timed out

        timestamp4_str = "2021-05-26T09:30:21.872"  # send
        timestamp5_str = "2021-05-26T09:31:51.872"  # signage - timeout

        timestamp6_str = "2021-05-26T09:44:52.872"  # recieve - (connect)

        line0 = msg_signage_point(timestamp0_str)
        line1 = msg_to_harvester(timestamp1_str, ip_address, node_id)
        line2 = msg_from_harvester(timestamp2_str, ip_address, node_id)
        line3 = msg_signage_point(timestamp3_str)

        ActionFinishedSignagePoint().apply(line0, chia_dog)
        ActionMessageToHarvester().apply(line1, chia_dog)
        ActionMessageFromHarvester().apply(line2, chia_dog)
        ActionFinishedSignagePoint().apply(line3, chia_dog)
        harvester_info = chia_dog.harvester_infos[node_id]
        self.assertFalse(harvester_info.timed_out)

        line4 = msg_to_harvester(timestamp4_str, ip_address, node_id)
        line5 = msg_signage_point(timestamp5_str)
        ActionMessageToHarvester().apply(line4, chia_dog)
        ActionFinishedSignagePoint().apply(line5, chia_dog)
        self.assertTrue(harvester_info.timed_out)
        self.assertEqual(harvester_info.n_overdue_responses, 1)

        line6 = msg_from_harvester(timestamp6_str, ip_address, node_id)
        ActionMessageFromHarvester().apply(line6, chia_dog)
        self.assertFalse(harvester_info.timed_out)

    def test_harvester_disconnect_times_reset_and_timeout(self):
        """
        This test is for the negative times which occured.
        Events:
        - send
        - disconnect XXX
        - send
        - send
        - connect XXX
        - recieve
        - recieve
        - send
        - recieve
        """
        # pylint: disable=too-many-locals

        actionOut = ActionMessageToHarvester()
        actionIn = ActionMessageFromHarvester()

        actionConnect = ActionHarvesterConnected()
        actionDisconnect = ActionHarvesterDisconnected()

        node_id = "d46fb9aaaa01f3aa3fc04f3e43231d35c3a1ddd4"
        ip_address = "57.22.39.97"
        timestamp1_str = "2021-05-26T09:38:01.872"  # send
        timestamp2_str = "2021-05-26T09:38:02.872"  # disconnect

        timestamp3_str = "2021-05-26T09:38:41.872"  # send

        timestamp4_str = "2021-05-26T09:38:56.872"  # connect

        timestamp5_str = "2021-05-26T09:43:39.872"  # recieve
        timestamp6_str = "2021-05-26T09:44:39.872"  # send
        timestamp7_str = "2021-05-26T09:45:39.872"  # recieve

        timestamp = datetime.fromisoformat(timestamp1_str)

        # pylint: disable=duplicate-code
        chia_dog = ChiaWatchdog("")
        chia_dog.harvester_infos = {
            node_id: FarmerHarvesterLogfile(
                node_id,
                ip_address,
                True,
                timestamp,
            )
        }

        harvester_info = list(chia_dog.harvester_infos.values())[0]

        # Here the testingbegins
        # send a challenge
        lineOut = msg_to_harvester(timestamp1_str, ip_address, node_id)
        actionOut.apply(lineOut, chia_dog)

        # disconnect
        lineDisconnect = msg_disconnect(timestamp2_str, ip_address, node_id)
        actionDisconnect.apply(lineDisconnect, chia_dog)

        self.assertFalse(harvester_info.is_connected)

        # send - late
        line = msg_signage_point(timestamp3_str)
        ActionFinishedSignagePoint().apply(line, chia_dog)
        lineOut = msg_to_harvester(timestamp3_str, ip_address, node_id)
        actionOut.apply(lineOut, chia_dog)
        self.assertFalse(harvester_info.is_connected)

        # connect
        lineConnect = msg_connect(timestamp4_str, ip_address, node_id)
        actionConnect.apply(lineConnect, chia_dog)
        self.assertTrue(harvester_info.is_connected)
        self.assertFalse(harvester_info.timed_out)

        # recieve  - late
        lineIn = msg_from_harvester(timestamp5_str, ip_address, node_id)
        actionIn.apply(lineIn, chia_dog)

        # send recieve
        lineOut = msg_to_harvester(timestamp6_str, ip_address, node_id)
        lineIn = msg_from_harvester(timestamp7_str, ip_address, node_id)

        actionOut.apply(lineOut, chia_dog)
        actionIn.apply(lineIn, chia_dog)


def msg_to_harvester(timestamp_str: str, ip_address: str, node_id: str) -> str:
    """ Get a fake log msg indicating a send msg to harvester """
    line = (
        f"{timestamp_str} farmer farmer_server              : DEBUG" +
        f"    -> new_signage_point_harvester to peer {ip_address} {node_id}"
    )
    return line


def msg_from_harvester(timestamp_str: str, ip_address: str, node_id: str) -> str:
    """ Get a fake log msg when a farmer receives data from a harvester """
    line = (
        f"{timestamp_str} farmer farmer_server              : DEBUG"
        + f"    <- farming_info from peer {node_id} {ip_address}"
    )
    return line


def msg_signage_point(timestamp_str: str) -> str:
    """ Get a fake log msg in case a new signage point has started """
    line = (
        f"{timestamp_str} full_node chia.full_node.full_node: INFO"
        + ":timer:  Finished signage point 19/64: CC: RC:"
    )
    return line


def msg_disconnect(timestamp_str: str, ip_address: str, node_id: str) -> str:
    """ Get a fake log msg for a disconnecting harvester to a farmer """
    line = (
        f"{timestamp_str} farmer farmer_server              : INFO"
        + f"     Connection closed: {ip_address},"
        + f" node id: {node_id}"
    )
    return line


def msg_connect(timestamp_str: str, ip_address: str, node_id: str) -> str:
    """ Get a fake log msg for a harvester connecting to a farmer """
    line = (
        f"{timestamp_str} farmer farmer_server           " +
        f"   : DEBUG    -> harvester_handshake to peer {ip_address} " +
        node_id
    )
    return line
