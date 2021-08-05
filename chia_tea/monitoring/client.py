import asyncio
from typing import Dict

from ..chia_watchdog.ChiaWatchdog import ChiaWatchdog
from ..chia_watchdog.run_watchdog import run_watchdog
from ..protobuf.generated.computer_info_pb2 import UpdateEvent
from ..protobuf.generated.config_pb2 import (
    _MONITORINGCONFIG_CLIENTCONFIG_SENDUPDATEEVERY, ChiaTeaConfig)
from ..protobuf.to_sqlite.generic import ProtoType
from ..utils.cli import parse_args
from ..utils.config import read_config
from .common import get_credentials_cert
from .MonitoringClient import MonitoringClient


def __get_collection_frequencies(config: ChiaTeaConfig) -> Dict[str, float]:
    """ Get the collection frequencies for updates to the server

    Parameters
    ----------
    config : ChiaTeaConfig
        config to use

    Returns
    -------
    collection_frequencies : Dict[str, float]
        update event name and frequency pairs

    Raises
    ------
    ValueError
        In case an invalid name not matching the proto schema
        was given
    """

    collection_frequencies = config.monitoring.client.send_update_every

    user_rate_limits = {}
    for field in _MONITORINGCONFIG_CLIENTCONFIG_SENDUPDATEEVERY.fields:
        field_value = getattr(collection_frequencies, field.name)
        user_rate_limits[field.name] = field_value

    update_event_var_names = tuple(
        field.name for field in UpdateEvent.DESCRIPTOR.fields
        if field.type == ProtoType.MESSAGE.value
    )

    for name, _ in user_rate_limits.items():
        if name not in update_event_var_names:
            err_msg = ("Config entry '{0}' is not valid." +
                       " Use one of {1}")
            raise ValueError(err_msg.format(
                name,
                ", ".join(update_event_var_names)
            ))

    return user_rate_limits


def main():

    args = parse_args(
        name="Chia Tea Monitoring Client",
        description=("This tool collects data about chia and the machine" +
                     "and sends them to the monitoring server.")
    )

    # load config
    config = read_config(args.config)

    # create the watchdog
    chia_logfile_path = config.chia.logfile_filepath
    watchdog = ChiaWatchdog(chia_logfile_path)

    # address of the server
    ip_address = config.monitoring.client.address
    port = config.monitoring.client.port

    # we disable auth during testing
    is_testing = config.development.testing

    cert = get_credentials_cert(is_testing, config) \
        if not is_testing else ""

    # throttling of the data collection
    collection_frequencies = __get_collection_frequencies(config)

    # throttling of general data collection
    collect_data_every = config.monitoring.client.collect_data_every

    # create client
    client = MonitoringClient(
        chia_dog=watchdog,
        ip_address=ip_address,
        port=port,
        collection_frequencies=collection_frequencies,
        collect_data_every=collect_data_every,
        credentials_cert=cert,
        machine_name=config.machine.name,
    )

    # setup event loops
    loop = asyncio.get_event_loop()
    loop.create_task(run_watchdog(watchdog))
    loop.create_task(client.start_sending_updates())
    loop.run_forever()


if __name__ == "__main__":
    main()
