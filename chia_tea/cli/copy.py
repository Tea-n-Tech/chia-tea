import typer

from ..utils.config import DEFAULT_CONFIG_FILEPATH
from ..copy.main import run_copy

copy_cmd = typer.Typer(invoke_without_command=True)


@copy_cmd.callback()
def copy(config: str = DEFAULT_CONFIG_FILEPATH) -> None:
    """
    Copy files from one place to another.

    For source and target directories please see the config file.
    """
    try:
        run_copy(filepath=config)
    except KeyboardInterrupt:
        typer.echo("Stopping copy")
    except Exception as err:
        typer.echo(f"Error: {err}")
        typer.Exit(1)
