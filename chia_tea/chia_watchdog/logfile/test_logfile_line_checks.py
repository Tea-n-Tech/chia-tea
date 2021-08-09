
import unittest
from datetime import datetime

from ..ChiaWatchdog import ChiaWatchdog
from .FarmerHarvesterLogfile import FarmerHarvesterLogfile
from .line_checks import (ActionHarvesterConnected,
                          ActionHarvesterDisconnected,
                          ActionHarvesterFoundProof, MessageFromHarvester, ActionFinishedSignagePoint,
                          MessageToHarvester)


class LineActionTester(unittest.TestCase):

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

        action = MessageToHarvester()

        node_id = "d46fb9aaaa01f3aa3fc04f3e43231d35c3a1ddd4"
        ip_address = "57.22.39.97"
        timestamp_str = "2021-05-26T09:37:13.872"

        line = (
            f"{timestamp_str} farmer farmer_server            " +
            "  : DEBUG    -> new_signage_point_harvester to peer " +
            f"{ip_address} {node_id}"
        )

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

        action = MessageFromHarvester()

        node_id = "d46fb9aaaa01f3aa3fc04f3e43231d35c3a1ddd4"
        ip_address = "57.22.39.97"
        timestamp_str = "2021-05-26T09:37:13.872"

        line = (
            f"{timestamp_str} farmer farmer_server            " +
            "  : DEBUG    <- farming_info from peer " +
            f"{node_id} {ip_address}"
        )

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

        action_out = MessageToHarvester()
        action_in = MessageFromHarvester()
        action_sgn = ActionFinishedSignagePoint()

        harvester_id = "befaebdf1129641d86bade79839d8616b584874c9a133e1f616633f3e6a2f9da"

        lineSignage = "2021-08-08T23:45:11.435 full_node chia.full_node.full_node: INFO    \
             :timer:  Finished signage point 19/64: CC:      \
                 RC: 7f11efb57cc2c97105c4e13099c$"

        # TODO

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
        actionOut = MessageToHarvester()
        actionIn = MessageFromHarvester()

        actionConnect = ActionHarvesterConnected()
        actionDisconnect = ActionHarvesterDisconnected()

        node_id = "d46fb9aaaa01f3aa3fc04f3e43231d35c3a1ddd4"
        ip_address = "57.22.39.97"
        timestamp1_str = "2021-05-26T09:38:39.872"  # send
        timestamp2_str = "2021-05-26T09:39:39.872"  # disconnect

        timestamp3_str = "2021-05-26T09:40:39.872"  # send
        timestamp4_str = "2021-05-26T09:42:39.872"  # connect

        timestamp5_str = "2021-05-26T09:43:39.872"  # recieve
        timestamp6_str = "2021-05-26T09:44:39.872"  # send
        timestamp7_str = "2021-05-26T09:45:39.872"  # recieve

        timestamp = datetime.fromisoformat(timestamp1_str)

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
        lineOut = (
            f"{timestamp1_str} farmer farmer_server           " +
            "   : DEBUG    -> new_signage_point_or_end_of_sub_slot to peer " +
            f"{ip_address} {node_id}"
        )

        actionOut.apply(lineOut, chia_dog)

        # disconnect
        lineDisconnect = (
            f"{timestamp2_str} farmer farmer_server              : INFO"
            + f"     Connection closed: {ip_address},"
            + f" node id: {node_id}"
        )
        actionDisconnect.apply(lineDisconnect, chia_dog)

        #self.assertEqual(len(harvester_info.time_of_incoming_messages), 0)
        #self.assertEqual(len(harvester_info.time_of_outgoing_messages), 0)
        #self.assertTrue(not harvester_info.is_connected)

        # send
        lineOut = (
            f"{timestamp3_str} farmer farmer_server           " +
            "   : DEBUG    -> new_signage_point_or_end_of_sub_slot to peer " +
            f"{ip_address} {node_id}"
        )
        actionOut.apply(lineOut, chia_dog)

        # connect
        lineConnect = (
            f"{timestamp4_str} farmer farmer_server           " +
            f"   : DEBUG    -> harvester_handshake to peer {ip_address} " +
            node_id)
        actionConnect.apply(lineConnect, chia_dog)

        # recieve with no send
        lineIn = (
            f"{timestamp5_str} farmer farmer_server           " +
            "   : DEBUG    <- new_signage_point from peer " +
            F"{node_id} {ip_address}"
        )

        actionIn.apply(lineIn, chia_dog)
        # send recieve

        lineOut = (
            f"{timestamp6_str} farmer farmer_server           " +
            "   : DEBUG    -> new_signage_point_or_end_of_sub_slot to peer " +
            f"{ip_address} {node_id}"
        )
        lineIn = (
            f"{timestamp7_str} farmer farmer_server           " +
            "   : DEBUG    <- new_signage_point from peer " +
            F"{node_id} {ip_address}"
        )

        actionOut.apply(lineOut, chia_dog)
        actionIn.apply(lineIn, chia_dog)
