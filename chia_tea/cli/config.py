import os
import typer
from ..utils.config import (
    DEFAULT_CONFIG_FILEPATH,
    DEFAULT_CONFIG_FOLDER,
    create_default_config,
    read_config,
)

from ..utils.ssl import create_certificate_pair
from ..utils.logger import get_logger

config_cmd = typer.Typer(no_args_is_help=True)


@config_cmd.command()
def init(
    filepath: str = DEFAULT_CONFIG_FILEPATH,
    create_certificates: bool = True,
    overwrite: bool = False,
) -> None:
    """Create the default chia-tea config file.

    If no filepath is specified the config is created in
    "~/.chia_tea/config/config.yml"
    """
    logger = get_logger(__name__)
    try:
        # create default config
        create_default_config(filepath=filepath, overwrite=overwrite)
        logger.info("Created config file: %s", filepath)

        # write certificates
        dirpath = os.path.dirname(filepath)
        key_path = os.path.join(dirpath, "server.key")
        cert_path = os.path.join(dirpath, "server.crt")
        if create_certificates:
            create_certificate_pair(key_path=key_path, cert_path=cert_path, overwrite=overwrite)

        logger.info("👍 Init Complete.")
    except FileExistsError as err:
        logger.error("⛈️  %s", str(err))
        logger.error("   You can enforce the creation with '--overwrite' if you like")
        typer.Exit(1)
    except Exception as err:
        logger.error("⛈️  %s", str(err))
        typer.Exit(1)


@config_cmd.command()
def location() -> None:
    """Print the filepath to the default location of the config file"""
    logger = get_logger(__name__)
    try:
        logger.info(os.path.expanduser(DEFAULT_CONFIG_FILEPATH))
    except Exception as err:
        logger.error("⛈️  %s", str(err))
        typer.Exit(1)


@config_cmd.command(name="create-certificates")
def create_certificates_cmd(dirpath: str = DEFAULT_CONFIG_FOLDER, overwrite: bool = False) -> None:
    """Create a certificate pair in the specified directory"""
    logger = get_logger(__name__)
    try:
        os.makedirs(dirpath, exist_ok=True)
        key_path = os.path.join(dirpath, "server.key")
        cert_path = os.path.join(dirpath, "server.crt")
        create_certificate_pair(key_path=key_path, cert_path=cert_path, overwrite=overwrite)
        logger.info("👍 Success")
    except Exception as err:
        logger.error("⛈️  %s", str(err))
        typer.Exit(1)


@config_cmd.command()
def validate(filepath: str) -> None:
    """Validate a config file.

    Raises an error in case the config file is not valid.
    """
    logger = get_logger(__name__)
    try:
        read_config(filepath)
        logger.info("👍 Config '%s' is valid", filepath)
    except Exception as err:
        logger.error("😢 Config '%s' is not valid: %s", filepath, str(err))
        typer.Exit(1)
