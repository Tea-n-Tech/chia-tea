import asyncio
import unittest
from datetime import datetime

from ..utils.testing import async_test
from .ChiaWatchdog import ChiaWatchdog
from .logfile.FarmerHarvesterLogfile import FarmerHarvesterLogfile
from .logfile.line_checks import ActionFarmedUnfinishedBlock


class TestChiaWatchdog(unittest.TestCase):
    @async_test
    async def test_readiness(self):
        dog = ChiaWatchdog("", "")

        async def assert_not_ready():
            with self.assertRaises(asyncio.TimeoutError):
                await asyncio.wait_for(dog.ready(), timeout=0.5)

        dog.set_chia_logfile_is_ready()
        await assert_not_ready()
        dog.set_madmax_logfile_is_ready()
        await assert_not_ready()
        dog.farmer_service.is_ready = True
        await assert_not_ready()
        dog.harvester_service.is_ready = True
        await assert_not_ready()
        dog.wallet_service.is_ready = True
        # raising an exception is an error case here
        await asyncio.wait_for(dog.ready(), timeout=0.5)

    def test_reward_found(self):
        action1 = ActionFarmedUnfinishedBlock()
        node_id = "65322a31ad01f3aa3fc04f3e43231d35c3a1ddd4"
        ip_address = "57.22.39.97"
        timestamp_str = "2021-05-26T09:37:13.872"
        timestamp = datetime.fromisoformat(timestamp_str)

        lineFirstRewardFound = (
            "07:39:12.978 full_node chia.full_node.full_node: "
            + "INFO     🍀 ️Farmed unfinished_block "
            + "6b2a9249ec4aa159c24498a00305012772d33e68a01d116c1110091f440e0cf6"
        )
        lineSecondRewardFound = (
            "07:39:12.978 full_node chia.full_node.full_node: "
            + "INFO     🍀 ️Farmed unfinished_block "
            + "6b2a9249ec4aa159c24498a00305012772d33e68a01d116c1110091f440e0cf7"
        )

        self.assertTrue(action1.is_match(lineFirstRewardFound))
        self.assertTrue(action1.is_match(lineSecondRewardFound))

        chia_dog = ChiaWatchdog("", "")
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
