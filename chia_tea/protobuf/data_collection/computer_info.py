
import asyncio
from datetime import datetime

from ...chia_watchdog.ChiaWatchdog import ChiaWatchdog
from ...protobuf.generated.computer_info_pb2 import ComputerInfo
from ...utils.logger import log_runtime_async
from .chia import (collect_connected_harvesters_to_farmer, collect_farmer_info,
                   collect_harvester_info, collect_harvester_plots,
                   collect_process_info, collect_wallet_info)
from .hardware import collect_cpu_info, collect_disk_info, collect_ram_info


@log_runtime_async(__file__)
async def collect_computer_info(
        machine_id: str,
        chia_dog: ChiaWatchdog) -> ComputerInfo:
    """ Collects all the info about the machine

    Parameters
    ----------
    machine_id : str
        id of the machine
    chia_dog : ChiaWatchdog
        chia watchdog to take data from

    Returns
    -------
    comuter_info : ComputerInfo
        info about the machine and it's chia related processes
    """

    (cpu_info,
     disks,
     ram_info,
     farmer_info,
     harvester_info,
     harvester_plots,
     wallet_info,
     chia_processes,
     connected_harvesters) = await asyncio.gather(
        collect_cpu_info(),
        collect_disk_info(),
        collect_ram_info(),
        collect_farmer_info(chia_dog),
        collect_harvester_info(chia_dog),
        collect_harvester_plots(chia_dog),
        collect_wallet_info(chia_dog),
        collect_process_info(),
        collect_connected_harvesters_to_farmer(chia_dog),
    )

    computer_info = ComputerInfo(
        timestamp=datetime.now().timestamp(),
        machine_id=machine_id,
        cpu=cpu_info,
        disks=disks,
        ram=ram_info,
        # plotting_progress=,
        farmer_harvesters=connected_harvesters,
        farmer=farmer_info,
        harvester=harvester_info,
        harvester_plots=harvester_plots,
        wallet=wallet_info,
        processes=chia_processes,
    )

    return computer_info
