
import os
import platform
from typing import List

import cpuinfo
import psutil

from ...protobuf.generated.hardware_pb2 import Cpu, Disk, Ram
from ...utils.logger import log_runtime_async


def __get_cpu_temp() -> float:
    """ Get the current cpu temperature

    Returns
    -------
    temp : float
        cpu temperature
    """
    temp = 0

    system_string = platform.system()

    # Linux
    if system_string == "Linux":
        temperatures = psutil.sensors_temperatures(fahrenheit=False)

        # cpu_thermal = raspberrypi
        # coretemp = common on linux
        cpu_temp_list = temperatures.get(
            'cpu_thermal') or temperatures.get('coretemp')
        if cpu_temp_list:
            temp_sum = sum(
                core_temp.current for core_temp in cpu_temp_list)
            temp = temp_sum / len(cpu_temp_list)
    # Mac
    elif system_string == "Darwin":
        pass
    # Windows
    elif system_string == "Windows":
        pass

    return temp


CPU_NAME = processor_name = cpuinfo.get_cpu_info().get(
    "brand_raw") or platform.processor()


@log_runtime_async(__file__)
async def collect_cpu_info() -> Cpu:
    """ Collect all info about the CPU

    Returns
    -------
    ram_info : Cpu
        info about the CPU
    """

    return Cpu(
        clock_speed=psutil.cpu_freq().current,
        usage=psutil.cpu_percent(),
        temperature=__get_cpu_temp(),
        name=CPU_NAME,
        n_vcores=os.cpu_count(),
    )


@log_runtime_async(__file__)
async def collect_ram_info() -> Ram:
    """ Collect all info about the RAM

    Returns
    -------
    ram_info : Ram
        info about the RAM
    """
    swap_memory = psutil.swap_memory()
    virtual_memory = psutil.virtual_memory()

    return Ram(
        total_ram=virtual_memory.total,
        used_ram=virtual_memory.used,
        total_swap=swap_memory.total,
        used_swap=swap_memory.used,
    )


@log_runtime_async(__file__)
async def collect_disk_info() -> List[Disk]:
    """ Collect all about the disks

    Returns
    -------
    disk_info_list : List[Disk]
        list with info about different disks
    """
    disk_info_list = []

    disk_partitions = psutil.disk_partitions()
    for partition in disk_partitions:
        if (partition.device.startswith("/dev/loop") or
                partition.mountpoint.startswith("/boot")):
            continue

        disk_usage = psutil.disk_usage(partition.mountpoint)

        disk_info_list.append(
            Disk(
                id=partition.mountpoint,
                total_space=disk_usage.total,
                used_space=disk_usage.used,
                device=partition.device,
                mountpoint=partition.mountpoint,
                fstype=partition.fstype,
                mount_options=partition.opts,
            )
        )

    return disk_info_list
