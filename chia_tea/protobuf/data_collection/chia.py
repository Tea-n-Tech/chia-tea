
from typing import Any, Dict, List

import psutil

from ...chia_watchdog.ChiaWatchdog import ChiaWatchdog
from ...protobuf.generated.chia_pb2 import (Farmer, Harvester, HarvesterPlot,
                                            HarvesterViewedFromFarmer, Process,
                                            Wallet)
from ...utils.logger import log_runtime_async


async def collect_connected_harvesters_to_farmer(
    chia_dog: ChiaWatchdog
) -> List[HarvesterViewedFromFarmer]:
    """ Converts harvester farmer data from watchdog to protobuf

    Parameters
    ----------
    chia_dog : ChiaWatchdog
        watchdog instance to get data from

    Returns
    -------
    farmer_harvesters : List[HarvesterViewedFromFarmer]
        harvester data reported by farmer in proto format
    """

    harvesters_rpc = {
        connected_harvester.node_id.hex(): connected_harvester
        for connected_harvester in chia_dog.farmer_service.connections
    }
    harvesters_logfile = chia_dog.harvester_infos

    # which harvesters do exist
    all_harvester_ids = set(harvesters_rpc.keys()) | \
        set(chia_dog.harvester_infos.keys())

    connected_harvesters = []
    for harvester_id in all_harvester_ids:

        kwargs: Dict[str, Any] = dict(
            id=harvester_id,
        )

        # get information from chia rpc
        connected_harvester = harvesters_rpc.get(harvester_id)
        if connected_harvester is not None:
            kwargs["connection_time"] = connected_harvester.creation_time
            kwargs["ip_address"] = connected_harvester.peer_host
            kwargs["n_plots"] = connected_harvester.n_plots
            # we don't use 'last_message_time' since it shows the last incoming or
            # outgoing message so we can't distinguish really.
            # kwargs["time_last_msg_sent"] = connected_harvester.last_message_time
        else:
            # there is no harvester process running anymore
            # thus we omit the data further down from the
            # logfile since we want a delete event in the db
            continue

        # get information written to logfile
        harvester_info = harvesters_logfile.get(harvester_id)
        if harvester_info:
            # don't append harvester info if it is not connected
            # anymore
            if not harvester_info.is_connected:
                continue
            kwargs["missed_challenges"] = harvester_info.n_overdue_responses
            kwargs["time_last_msg_received"] = harvester_info.time_last_incoming_msg or 0.
            kwargs["time_last_msg_sent"] = harvester_info.time_last_outgoing_msg or 0.

        connected_harvesters.append(
            HarvesterViewedFromFarmer(
                **kwargs,
            )
        )

    return connected_harvesters


@log_runtime_async(__file__)
async def collect_farmer_info(chia_dog: ChiaWatchdog) -> Farmer:
    """ Collects info about the farmer

    Parameters
    ----------
    chia_dog : ChiaWatchdog
        chia watchdog to take data from

    Returns
    -------
    farmer_info : Farmer
        info about the farmer running on the system
    """
    return Farmer(
        is_running=chia_dog.farmer_service.is_running,
        # connected_harvesters=,
        # total_challenges=,
    )


@log_runtime_async(__file__)
async def collect_harvester_info(
    chia_dog: ChiaWatchdog
) -> Harvester:
    """ Collects info about the farmer

    Parameters
    ----------
    chia_dog : ChiaWatchdog
        chia watchdog to take data from

    Returns
    -------
    info : Harvester
        info about the harvester running on the system
    plots : List[HarvesterPlot]
        list of plots on the harvester
    """

    return Harvester(
        is_running=chia_dog.harvester_service.is_running,
        n_proofs=chia_dog.harvester_service.n_proofs,
    )


@log_runtime_async(__file__)
async def collect_harvester_plots(
    chia_dog: ChiaWatchdog
) -> List[HarvesterPlot]:
    """ Collects info about the harvester plots

    Parameters
    ----------
    chia_dog : ChiaWatchdog
        chia watchdog to take data from

    Returns
    -------
    plots : List[HarvesterPlot]
        list of plots on the harvester
    """

    plots: List[HarvesterPlot] = []
    for plot_response in chia_dog.harvester_service.plots:
        plots.append(
            HarvesterPlot(
                id=plot_response["plot_public_key"],
                plot_seed=plot_response["plot-seed"],
                filename=plot_response["filename"],
                filesize=plot_response["file_size"],
                pool_contract_puzzle_hash=plot_response["pool_contract_puzzle_hash"],
                pool_public_key=plot_response["pool_public_key"],
                size=plot_response["size"],
                time_modified=plot_response["time_modified"],
            )
        )

    return plots


@log_runtime_async(__file__)
async def collect_wallet_info(chia_dog: ChiaWatchdog) -> Wallet:
    """ Collects info about the farmer

    Parameters
    ----------
    chia_dog : ChiaWatchdog
        chia watchdog to take data from

    Returns
    -------
    wallet_info : Wallet
        info about the wallet running on the system
    """
    return Wallet(
        is_running=chia_dog.wallet_service.is_running,
        is_synced=chia_dog.wallet_service.is_synced,
    )


@log_runtime_async(__file__)
async def collect_process_info() -> List[Process]:
    """ Collect data about every chia related process
    running on the machine

    Returns
    -------
    processes : List[Process]
        List of processes
    """

    process_names_to_filter_for = (
        "chia",
        "chia_harvester",
        "chia_farmer",
        "chia_wallet",
        "chia_daemon",
        "chia_full_node",
    )

    processes: List[Process] = []

    for process in psutil.process_iter():
        if not process.name() in process_names_to_filter_for:
            continue

        try:
            meminfo = process.memory_info()

            # network_connections = [
            #     "{ip}:{port}".format(
            #         ip=connection.raddr[0],
            #         port=connection.raddr[0],
            #     )
            #     for connection in process.connections()
            # ]

            processes.append(
                Process(
                    name=process.name(),
                    executable=process.exe(),
                    command="".join(process.cmdline()),
                    create_time=process.create_time(),
                    id=process.pid,
                    cpu_usage=process.cpu_percent(),
                    used_physical_ram=meminfo.rss,
                    used_virtual_ram=meminfo.vms,
                    opened_files=", ".join(
                        file.path for file in process.open_files()),
                    # network_connections=network_connections,
                )
            )
        except (
            psutil.NoSuchProcess,
            psutil.PermissionError,
            psutil.AccessDenied,
        ):
            pass

    return processes
