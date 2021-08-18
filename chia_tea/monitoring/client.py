import asyncio

from ..chia_watchdog.ChiaWatchdog import ChiaWatchdog
from ..chia_watchdog.run_watchdog import run_watchdog
from ..utils.cli import parse_args
from ..utils.config import read_config
from .common import get_credentials_cert
from .MonitoringClient import MonitoringClient


def main():
    """ This function starts the chia tea client """
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

    # we disable auth during testing
    is_testing = config.development.testing

    cert = get_credentials_cert(is_testing, config) \
        if not is_testing else ""

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


if __name__ == "__main__":
    main()
