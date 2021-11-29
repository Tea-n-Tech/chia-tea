import typer

from ..monitoring.run_server import run_monitoring_server
from ..utils.config import DEFAULT_CONFIG_FILEPATH, read_config
from ..utils.logger import get_logger
from ..monitoring.run_client import run_monitoring_client
from ..discord.bot import run_discord_bot
from ..copy.main import run_copy


start_cmd = typer.Typer(
    no_args_is_help=True,
    help="Start chia-tea tools and processes.",
)


@start_cmd.command(name="copy")
def copy(config: str = DEFAULT_CONFIG_FILEPATH) -> None:
    """Copy files from one place to another.

    For source and target directories please see the config file.
    You can get the standard config-file filepath by running
    `chia-tea config location`.
    """
    try:
        config = read_config(filepath=config)
        run_copy(config=config)
    except KeyboardInterrupt:
        typer.echo("Stopping copy")
    except Exception as err:
        typer.echo(f"Error: {err}")
        raise typer.Exit(1)


@start_cmd.command("monitoring-client")
def client_cmd(config: str = DEFAULT_CONFIG_FILEPATH):
    """Starts the monitoring client observing chia and the machine"""
    logger = get_logger(__name__)

    try:
        config = read_config(config)
        run_monitoring_client(config)
    except KeyboardInterrupt:
        # just stopping it, that is ok
        pass
    except Exception as err:
        logger.error("Error: %s", str(err))
    finally:
        logger.info("Shutting down monitoring client.")


@start_cmd.command("monitoring-server")
def server_cmd(config: str = DEFAULT_CONFIG_FILEPATH):
    """Starts the server receiving and storing monitoring data"""
    logger = get_logger(__name__)

    try:
        config = read_config(config)
        run_monitoring_server(config)
    except KeyboardInterrupt:
        # just stopping it, that is ok
        pass
    except Exception as err:
        logger.error("Error: %s", str(err))
    finally:
        logger.info("Shutting down monitoring server.")


@start_cmd.command("discord-bot")
def start_discord_bot(config: str = DEFAULT_CONFIG_FILEPATH):
    """
    Start the discord bot watching the monitoring database.
    """

    # load config
    config = read_config(config)

    discord_token = config.discord.token
    channel_id = config.discord.channel_id

    run_discord_bot(discord_token, channel_id)
