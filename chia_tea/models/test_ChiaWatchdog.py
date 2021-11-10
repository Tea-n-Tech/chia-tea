import asyncio
import unittest

from ..utils.testing import async_test
from .ChiaWatchdog import ChiaWatchdog


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
