import typer

from ..monitoring.run_server import run_monitoring_server
from ..utils.config import DEFAULT_CONFIG_FILEPATH, read_config
from ..monitoring.run_client import run_monitoring_client
from ..discord.bot import run_discord_bot
from ..copy.main import run_copy


start_cmd = typer.Typer(
    no_args_is_help=True,
    help="Start chia-tea tools and processes.",
)


@start_cmd.command(name="copy")
def copy_cmd(config: str = DEFAULT_CONFIG_FILEPATH) -> None:
    """Copy files from one place to another.

    For source and target directories please see the config file.
    You can get the standard config-file filepath by running
    `chia-tea config location`.
    """
    try:
        config = read_config(filepath=config)
        run_copy(config=config)
    except KeyboardInterrupt:
        # just stopping it, that is ok
        pass
    except Exception as err:
        typer.echo(f"⛈️  Error: {err}")
        raise typer.Exit(1)
    finally:
        typer.echo("Stopping copy")


@start_cmd.command("monitoring-client")
def monitoring_client_cmd(config: str = DEFAULT_CONFIG_FILEPATH):
    """Starts the monitoring client observing chia and the machine"""

    exit_code = 0
    try:
        config = read_config(filepath=config)
        run_monitoring_client(config)
    except KeyboardInterrupt:
        # just stopping it, that is ok
        pass
    except Exception as err:
        typer.echo(f"⛈️  Error: {err}")
        exit_code = 1
    finally:
        typer.echo("Shutting down monitoring client.")
        raise typer.Exit(exit_code)


@start_cmd.command("monitoring-server")
def monitoring_server_cmd(config: str = DEFAULT_CONFIG_FILEPATH):
    """Starts the server receiving and storing monitoring data"""

    exit_code = 0
    try:
        config = read_config(filepath=config)
        run_monitoring_server(config)
    except KeyboardInterrupt:
        # just stopping it, that is ok
        pass
    except Exception as err:
        typer.echo(f"⛈️  Error: {err}")
        exit_code = 1
    finally:
        typer.echo("Shutting down monitoring server.")
        raise typer.Exit(exit_code)


@start_cmd.command("discord-bot")
def discord_bot_cmd(config: str = DEFAULT_CONFIG_FILEPATH):
    """
    Start the discord bot watching the monitoring database.
    """

    exit_code = 0
    try:
        config = read_config(filepath=config)
        run_discord_bot(config.discord.token, config.discord.channel_id)
    except KeyboardInterrupt:
        # just stopping it, that is ok
        pass
    except Exception as err:
        typer.echo(f"⛈️  Error: {err}")
        exit_code = 1
    finally:
        typer.echo("Shutting down discord-bot.")
        raise typer.Exit(exit_code)
