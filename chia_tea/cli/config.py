
import typer
from chia_tea.utils.config import (DEFAULT_CONFIG_FILEPATH,
                                   create_default_config, read_config)

config_cmd = typer.Typer()

@config_cmd.command()
def init(
        filepath: str = DEFAULT_CONFIG_FILEPATH,
        overwrite: bool = False,
    ) -> None:
    """ Create the default chia-tea config file.

    If no filepath is specified the config is created in
    "~/.chia_tea/config/config.yml"
    """
    try:
        create_default_config(filepath, overwrite=overwrite)
        typer.echo(f"👍 Created config file: {filepath}")
    except Exception as err:
        typer.echo(f"⛈️  {err}")

@config_cmd.command()
def validate(filepath: str) -> None:
    """ Validate a config file.

    Raises an error in case the config file is not valid.
    """
    try:
        read_config(filepath)
        typer.echo("👍 Config '%s' is valid" % filepath)
    except Exception as err:
        typer.echo("😢 Config '%s' is not valid: %s" % (filepath, err))
        typer.Exit(1)
