
import unittest
from datetime import date, datetime, timedelta

from .ChiaWatchdog import ChiaWatchdog
from .logfile.FarmerHarvesterLogfile import FarmerHarvesterLogfile
from .logfile.line_checks import ActionFarmedUnfinishedBlock


class TestChiaWatchdog(unittest.TestCase):

    def test_nightly_reset(self):

        watchdog = ChiaWatchdog("")

        # add a random harvester
        harvester_info = FarmerHarvesterLogfile(
            harvester_id="my_id",
            ip_address="127.0.0.1",
            is_connected=True,
            last_update=datetime.now()
        )
        watchdog.harvester_infos = {
            harvester_info.harvester_id: harvester_info
        }

        # set yesterday as date
        today = date.today()
        yesterday = today - timedelta(days=1)
        watchdog.date_last_reset = yesterday

        # test if reset is correctly detected
        self.assertTrue(watchdog.is_reset_time())

        # test if data is resettet
        watchdog.reset_data()
        self.assertDictEqual(watchdog.harvester_infos, {})

        # check if reset is not executed anymore
        should_be = {
            harvester_info.harvester_id: harvester_info
        }
        watchdog.harvester_infos = should_be
        self.assertFalse(watchdog.is_reset_time())
        self.assertDictEqual(watchdog.harvester_infos, should_be)

    def test_reward_found(self):
        action1 = ActionFarmedUnfinishedBlock()
        node_id = "65322a31ad01f3aa3fc04f3e43231d35c3a1ddd4"
        ip_address = "57.22.39.97"
        timestamp_str = "2021-05-26T09:37:13.872"
        timestamp = datetime.fromisoformat(timestamp_str)

        lineFirstRewardFound = (
            "07:39:12.978 full_node chia.full_node.full_node: " +
            "INFO     🍀 ️Farmed unfinished_block " +
            "6b2a9249ec4aa159c24498a00305012772d33e68a01d116c1110091f440e0cf6"
        )
        lineSecondRewardFound = (
            "07:39:12.978 full_node chia.full_node.full_node: " +
            "INFO     🍀 ️Farmed unfinished_block " +
            "6b2a9249ec4aa159c24498a00305012772d33e68a01d116c1110091f440e0cf7"
        )

        self.assertTrue(action1.is_match(lineFirstRewardFound))
        self.assertTrue(action1.is_match(lineSecondRewardFound))

        chia_dog = ChiaWatchdog("")
        chia_dog.harvester_infos = {
            node_id: FarmerHarvesterLogfile(
                node_id,
                ip_address,
                True,
                timestamp,
            )
        }

        self.assertEqual(len(chia_dog.farmed_blocks), 0)
        action1.apply(lineFirstRewardFound, chia_dog)
        self.assertEqual(len(chia_dog.farmed_blocks), 1)
        action1.apply(lineSecondRewardFound, chia_dog)
        self.assertEqual(len(chia_dog.farmed_blocks), 2)
        action1.apply(lineSecondRewardFound, chia_dog)
        self.assertEqual(len(chia_dog.farmed_blocks), 2)
