import asyncio

from ..models.ChiaWatchdog import ChiaWatchdog
from ..protobuf.generated.config_pb2 import ChiaTeaConfig
from ..watchdog.run_watchdog import run_watchdog
from .common import get_credentials_cert
from .MonitoringClient import MonitoringClient


def run_monitoring_client(config: ChiaTeaConfig) -> None:
    """This function starts the chia tea client

    Parameters
    ----------
    config : ChiaTeaConfig
        the configuration used to run the client
    """

    # create the watchdog
    watchdog = ChiaWatchdog(
        config.chia.logfile_filepath,
        config.chia.madmax_logfile,
    )

    # we disable auth during testing
    is_testing = config.development.testing

    cert = get_credentials_cert(is_testing, config) if not is_testing else ""

    # create client
    client = MonitoringClient(
        chia_dog=watchdog,
        config=config.monitoring.client,
        credentials_cert=cert,
        machine_name=config.machine.name,
    )

    # setup event loops
    loop = asyncio.get_event_loop()
    loop.create_task(run_watchdog(watchdog))
    loop.create_task(client.start_sending_updates())
    loop.run_forever()
