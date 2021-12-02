import os
import typer
from ..utils.config import (
    DEFAULT_CONFIG_FILEPATH,
    DEFAULT_CONFIG_FOLDER,
    create_default_config,
    read_config,
)

from ..utils.ssl import create_certificate_pair

config_cmd = typer.Typer(no_args_is_help=True)


@config_cmd.command()
def init(
    filepath: str = DEFAULT_CONFIG_FILEPATH,
    overwrite: bool = False,
) -> None:
    """Create the default chia-tea config file.

    If no filepath is specified the config is created in
    "~/.chia_tea/config/config.yml"
    """
    try:
        # create default config
        create_default_config(filepath=filepath, overwrite=overwrite)
        typer.echo(f"👍 Created config file '{filepath}'")
    except FileExistsError as err:
        typer.echo(f"⛈️  {err}")
        typer.echo("   You can enforce the creation with '--overwrite' if you like.")
        raise typer.Exit(1)
    except Exception as err:
        typer.echo(f"⛈️  {err}")
        raise typer.Exit(1)


@config_cmd.command()
def location() -> None:
    """Print the filepath to the default location of the config file"""
    try:
        typer.echo(os.path.expanduser(DEFAULT_CONFIG_FILEPATH))
    except Exception as err:
        typer.echo(f"⛈️  {err}")
        raise typer.Exit(1)


@config_cmd.command(name="create-certificates")
def create_certificates_cmd(
    dirpath: str = DEFAULT_CONFIG_FOLDER, common_name: str = "localhost", overwrite: bool = False
) -> None:
    """Create a certificate pair in the specified directory"""
    try:
        os.makedirs(dirpath, exist_ok=True)
        key_path = os.path.join(dirpath, "server.key")
        cert_path = os.path.join(dirpath, "server.crt")
        create_certificate_pair(
            key_path=key_path, cert_path=cert_path, overwrite=overwrite, common_name=common_name
        )
    except Exception as err:
        typer.echo(f"⛈️  {err}")
        raise typer.Exit(1)


@config_cmd.command()
def validate(filepath: str) -> None:
    """Validate a config file.

    Raises an error in case the config file is not valid.
    """
    try:
        read_config(filepath)
        typer.echo("👍 Config '%s' is valid", filepath)
    except Exception as err:
        typer.echo("😢 Config '%s' is not valid: %s", filepath, str(err))
        raise typer.Exit(1)
