import typer

from ..monitoring.run_server import run_server
from ..utils.config import DEFAULT_CONFIG_FILEPATH, read_config
from ..utils.logger import get_logger
from ..monitoring.run_client import run_client

monitoring_cmd = typer.Typer(
    no_args_is_help=True,
    help="This tool collects data about chia and the machine"
    + "and sends them to the monitoring server.",
)


@monitoring_cmd.command("client")
def client_cmd(config: str = DEFAULT_CONFIG_FILEPATH):
    """Starts the monitoring client observing chia and the machine"""
    logger = get_logger(__name__)

    try:
        config = read_config(config)
        run_client(config)
    except KeyboardInterrupt:
        # just stopping it, that is ok
        pass
    except Exception as err:
        logger.error("Error: %s", str(err))
    finally:
        logger.info("Shutting down monitoring client.")


@monitoring_cmd.command("server")
def server_cmd(config: str = DEFAULT_CONFIG_FILEPATH):
    """Starts the server receiving and storing monitoring data"""
    logger = get_logger(__name__)

    try:
        config = read_config(config)
        run_server(config)
    except KeyboardInterrupt:
        # just stopping it, that is ok
        pass
    except Exception as err:
        logger.error("Error: %s", str(err))
    finally:
        logger.info("Shutting down monitoring server.")
