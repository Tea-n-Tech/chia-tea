import asyncio

import typer

from ..models.ChiaWatchdog import ChiaWatchdog
from ..monitoring.common import get_credentials_cert
from ..monitoring.MonitoringClient import MonitoringClient
from ..monitoring.server import start_server
from ..utils.config import DEFAULT_CONFIG_FILEPATH, read_config
from ..utils.logger import get_logger
from ..watchdog.run_watchdog import run_watchdog

monitoring_cmd = typer.Typer(
    no_args_is_help=True,
    help="This tool collects data about chia and the machine"
    + "and sends them to the monitoring server.",
)


@monitoring_cmd.command("client")
def client_cmd(config: str = DEFAULT_CONFIG_FILEPATH):
    """Starts the monitoring client observing chia and the machine"""

    # load config
    config = read_config(config)

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


@monitoring_cmd.command("server")
def server_cmd(config: str = DEFAULT_CONFIG_FILEPATH):
    """Starts the server receiving and storing monitoring data"""

    try:
        # load config
        config = read_config(config)

        # setup logger
        logger = get_logger(__name__)

        # start the server
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_server(config))

    except KeyboardInterrupt:
        logger.info("Stopped server.")
