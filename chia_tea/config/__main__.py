import argparse
import os
import sys

from ..utils.cli import str2bool
from ..utils.config import get_default_config, read_config, save_config
from ..utils.logger import get_logger

module_name = "chia_tea.config"


def _parse_args() -> argparse.Namespace:
    ''' Parse the arguments from the command line

    Returns
    -------
    args : argparse.Namespace
        parsed arguments
    '''

    parser = argparse.ArgumentParser(
        prog="Chia-Tea Config",
        description=(
            "This tool is used to either create a default config" +
            " or validate an existing config."
        ))

    parser.add_argument("config",
                        help="Path to the config file")
    parser.add_argument("--generate",
                        type=str2bool,
                        nargs="?",
                        default=False,
                        const=True,
                        help="Generate a default config")
    parser.add_argument("--validate",
                        type=str2bool,
                        nargs="?",
                        default=False,
                        const=True,
                        help="Generate a default config")
    parser.add_argument("--overwrite",
                        type=str2bool,
                        nargs="?",
                        default=False,
                        const=True,
                        help="Generate a default config")

    if len(sys.argv) < 1:
        parser.print_help()
        sys.exit(0)

    return parser.parse_args(sys.argv[1:])


def _generate_default_config(
    filepath: str,
    overwrite: bool,
):
    """ Generate a default config on the specified path

    Parameters
    ----------
    filepath : str
        path where to create the default config
    overwrite : bool
        whether to overwrite in case the file already exists
    """
    logger = get_logger(module_name)

    if os.path.isfile(filepath) and not overwrite:
        err_msg = "Config file '%s' does already exist. Use '--overwrite' to overwrite this file."
        logger.error(err_msg, filepath)
        sys.exit(1)

    save_config(
        filepath=filepath,
        config=get_default_config(),
    )


def _validate_config(filepath: str):
    """ Validate a chia-tea config

    Parameters
    ----------
    filepath : str
        path to the config file
    """
    logger = get_logger(module_name)

    try:
        read_config(filepath)
        logger.info("👍 Config '%s' is valid", filepath)
    except Exception as err:
        logger.error(str(err))
        sys.exit(1)


def main():
    """ Main function for the config cli
    """
    args = _parse_args()

    # generate a deffault config
    if args.generate:
        _generate_default_config(
            args.config,
            args.overwrite,
        )

    # validate the config
    if args.validate:
        _validate_config(
            args.config
        )


if __name__ == "__main__":
    main()
