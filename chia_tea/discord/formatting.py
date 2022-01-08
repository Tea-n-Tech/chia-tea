from datetime import datetime
from typing import List

from ..protobuf.generated.chia_pb2 import (
    FullNode,
    Harvester,
    HarvesterPlot,
    HarvesterViewedFromFarmer,
    PlotInProgress,
)
from ..protobuf.generated.hardware_pb2 import Cpu, Disk, Ram
from ..protobuf.generated.machine_info_pb2 import MachineInfo
from ..utils.timing import format_time_since, format_timedelta_from_secs


def format_memory_size(n_bytes: float, suffix: str = "B"):
    """Formats a memory size number

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
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(n_bytes) < 1024.0:
            return "%3.1f%s%s" % (n_bytes, unit, suffix)
        n_bytes /= 1024.0
    return "%.1f%s%s" % (n_bytes, "Yi", suffix)


def cpu_pb2_as_markdown(cpu: Cpu) -> str:
    """Formats a protobuf cpu as markdown

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
    """Formats a protobuf ram as markdown

    Parameters
    ----------
    ram : Ram
        ram instance with data

    Returns
    -------
    ram_as_string : str
        ram info as markdown string
    """

    used_percent = 0.0
    try:
        used_percent = ram.used_ram / ram.total_ram * 100
    except ZeroDivisionError:
        pass
    swap_percent = 0.0
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
    """Formats a protobuf HarvesterViewedFromFarmer as markdown

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
        last_answer=format_timedelta_from_secs(now_timestamp - harvester.time_last_msg_received),
        harvester_id=harvester.id[:8],
        missed_challenges=harvester.missed_challenges,
        n_plots=harvester.n_plots,
    )


def disk_pb2_as_markdown(disk: Disk) -> str:
    """Formats a protobuf HarvesterViewedFromFarmer as markdown

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
    free_memory_as_str = format_memory_size(disk.total_space - disk.used_space)
    return f"        {usage_percent:3.1f}% {disk.id} ({free_memory_as_str} free)"


def harvester_pb2_as_markdown(
    machine: MachineInfo,
    harvester: Harvester,
    plots: List[HarvesterPlot],
    disks: List[Disk],
) -> str:
    """Formats a protobuf Harvester as markdown

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
    disk_msgs = [disk_pb2_as_markdown(disk) for disk in disks]

    return """
  🚜 Harvester {machine}
     🍀 proofs: {n_proofs}
     🌾 plots: {n_plots}
     🌾 size of plots: {total_size}
     💽 disks:
{disk_msgs}""".format(
        machine=get_machine_info_name(machine),
        n_plots=len(plots),
        n_proofs=harvester.n_proofs,
        total_size=format_memory_size(total_size),
        disk_msgs="\n".join(disk_msgs),
    )


def full_node_pb2_as_markdown(
    machine: MachineInfo,
    full_node: FullNode,
) -> str:
    """Formats a protobuf Harvester as markdown

    Parameters
    ----------
    machine : MachineInfo
        info about the machine including name and ip
    full_node : FullNode
        full_node instance with data

    Returns
    -------
    harvester_as_string : str
        harvester info as markdown string
    """

    sync_msg = "⚠️  not synced" if not full_node.is_synced else "🟢 synchronized"
    sync_progress_percent = (
        full_node.sync_node_height / full_node.sync_blockchain_height
        if full_node.sync_blockchain_height != 0
        else 0
    )

    return """
  🏡 Full Node {machine}
     {sync_msg}
     ⏳ progress: {node_progress}/{blockchain_progress} ({progress_percent:.2f} %)
""".format(
        machine=get_machine_info_name(machine),
        sync_msg=sync_msg,
        node_progress=full_node.sync_node_height,
        blockchain_progress=full_node.sync_blockchain_height,
        progress_percent=sync_progress_percent,
    )


def plot_in_progress_pb2_as_markdown(plot_in_progress: PlotInProgress) -> str:
    """Formats a protobuf PlotInProgress as markdown

    Parameters
    ----------
    plot_in_progress: PlotInProgress
        plot in progress to be formatted in markdown

    Returns
    -------
    msg : str
        plot_in_progress as markdown string
    """

    start_time_dt = datetime.fromtimestamp(plot_in_progress.start_time)

    return "\n".join(
        (
            f"  - 🌽 Plot {plot_in_progress.id[:12]}...",
            f"       Since: {format_time_since(start_time_dt)}",
            f"       State: {plot_in_progress.state}",
            f"       Progress: {plot_in_progress.progress*100:.1f}%",
        )
    )


def get_machine_info_name(machine: MachineInfo) -> str:
    """Get a nicely formatted name for a machine info

    Parameters
    ----------
    machine : MachineInfo
        machine info to get a name of

    Returns
    -------
    name : str
        nicely formatted name of the machine info
    """

    return "{name} {id} ({ip})".format(
        name=f"{machine.name} -" if machine.name else "",
        id=str(machine.machine_id)[:10],
        ip=machine.ip_address,
    )
