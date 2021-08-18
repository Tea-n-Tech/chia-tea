
from datetime import datetime
from typing import List

from chia_tea.discord.notifications.common import get_machine_info_name
from chia_tea.protobuf.generated.machine_info_pb2 import MachineInfo

from ...protobuf.generated.chia_pb2 import (Harvester, HarvesterPlot,
                                            HarvesterViewedFromFarmer)
from ...protobuf.generated.hardware_pb2 import Cpu, Disk, Ram
from ...utils.timing import format_timedelta_from_secs


def format_memory_size(n_bytes: float, suffix: str = 'B'):
    """ Formats a memory size number

    Parameters
    ----------
    n_bytes : float
        bytes to format
    suffix : string
        suffix of the memory

    Notes
    -----
        Thanks Fred @ Stackoverflow:
        https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size
    """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(n_bytes) < 1024.0:
            return "%3.1f%s%s" % (n_bytes, unit, suffix)
        n_bytes /= 1024.0
    return "%.1f%s%s" % (n_bytes, 'Yi', suffix)


def cpu_pb2_as_markdown(cpu: Cpu) -> str:
    """ Formats a protobuf cpu as markdown

    Parameters
    ----------
    cpu : Cpu
        cpu instance with data

    Returns
    -------
    cpu_as_string : str
        cpu info as markdown string
    """

    return """   __CPU__
      name:  {name}
      cores: {cores}
      usage: {usage:.1f}%
      temp:  {temperature:.0f} deg
      clock: {speed:.0f} Mhz""".format(
        name=cpu.name,
        cores=cpu.n_vcores,
        usage=cpu.usage,
        temperature=cpu.temperature,
        speed=cpu.clock_speed,
    )


def ram_pb2_as_markdown(ram: Ram) -> str:
    """ Formats a protobuf ram as markdown

    Parameters
    ----------
    ram : Ram
        ram instance with data

    Returns
    -------
    ram_as_string : str
        ram info as markdown string
    """

    used_percent = 0.
    try:
        used_percent = ram.used_ram / ram.total_ram * 100
    except ZeroDivisionError:
        pass
    swap_percent = 0.
    try:
        swap_percent = ram.used_swap / ram.total_swap * 100
    except ZeroDivisionError:
        pass

    return """   __RAM__
      total: {total}
      used:  {used:.1f}%
      swap:  {swap:.1f}%
      """.format(
        total=format_memory_size(ram.total_ram),
        used=used_percent,
        swap=swap_percent,
    )


def farmer_harvester_pb2_as_markdown(harvester: HarvesterViewedFromFarmer) -> str:
    """ Formats a protobuf HarvesterViewedFromFarmer as markdown

    Parameters
    ----------
    harvester : HarvesterViewedFromFarmer
        farmer harvester instance with data

    Returns
    -------
    harvester_as_string : str
        farmer harvester info as markdown string
    """
    now_timestamp = datetime.now().timestamp()

    return """
  Harvester *{harvester_id}*
     🌐 ip address:  {ip_address}
     📡 last answer: {last_answer} ago
     🚆 missed challenges: {missed_challenges}
     🌾 plots: {n_plots}""".format(
        ip_address=harvester.ip_address,
        last_answer=format_timedelta_from_secs(
            now_timestamp - harvester.time_last_msg_received),
        harvester_id=harvester.id[:8],
        missed_challenges=harvester.missed_challenges,
        n_plots=harvester.n_plots,
    )


def disk_pb2_as_markdown(disk: Disk) -> str:
    """ Formats a protobuf HarvesterViewedFromFarmer as markdown

    Parameters
    ----------
    disk : Disk
        disk instance with data

    Returns
    -------
    disk_as_string : str
        disk info as markdown string
    """
    usage_percent = 0
    try:
        usage_percent = disk.used_space / disk.total_space * 100
    except ZeroDivisionError:
        pass
    return f"        {usage_percent:3.1f}% {disk.id}"


def harvester_pb2_as_markdown(
    machine: MachineInfo,
    harvester: Harvester,
    plots: List[HarvesterPlot],
    disks: List[Disk],
) -> str:
    """ Formats a protobuf Harvester as markdown

    Parameters
    ----------
    machine : MachineInfo
        info about the machine including name and ip
    harvester : Harvester
        harvester instance with data
    plots : List[HarvesterPlot]
        plots of the harvester
    disks : List[Disk]
        disks of the harvester

    Returns
    -------
    harvester_as_string : str
        harvester info as markdown string
    """

    total_size = sum(plot.filesize for plot in plots)
    disk_msgs = [
        disk_pb2_as_markdown(disk) for disk in disks
    ]

    return """
  🚜 Harvester {machine}
     🍀 proofs: {n_proofs}
     🌾 plots: {n_plots}
     🌾 size of plots: {total_size}
     💽 disks:
{disk_msgs}
     """.format(
        machine=get_machine_info_name(machine),
        n_plots=len(plots),
        n_proofs=harvester.n_proofs,
        total_size=format_memory_size(total_size),
        disk_msgs="\n".join(disk_msgs)
    )
