import asyncio

from ..ChiaWatchdog import ChiaWatchdog
from .update_from_farmer import update_from_farmer
from .update_from_harvester import update_from_harvester
from .update_from_wallet import update_from_wallet


async def update_directly_from_chia(chia_dog: ChiaWatchdog):
    """ Update the chia watchdog directly with data received from chia

    Parameters
    ----------
    chia_dog : ChiaWatchdog
        watchdog instance to be modified
    """
    await asyncio.gather(
        update_from_farmer(chia_dog=chia_dog),
        update_from_wallet(chia_dog=chia_dog),
        update_from_harvester(chia_dog=chia_dog),
    )
