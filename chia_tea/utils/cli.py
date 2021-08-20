import argparse
import sys


def str2bool(value) -> bool:
    ''' Converts some value from the cmd line to a boolean
    Parameters
    ----------
    value: `str` or `bool`
    Returns
    -------
    bool_value: `bool`
        value as boolean
    '''

    if isinstance(value, bool):
        return value

    if value.lower() in ('yes', 'true', 't', 'y', '1'):
        return True

    if value.lower() in ('no', 'false', 'f', 'n', '0'):
        return False

    raise argparse.ArgumentTypeError('Boolean value expected.')


def parse_args(name: str, description: str) -> argparse.Namespace:
    ''' Parse the arguments from the command line

    Parameters
    ----------
    name : str
        name of the cli
    description : str
        describe shortly what the cli does

    Returns
    -------
    args : argparse.Namespace
        parsed arguments
    '''

    parser = argparse.ArgumentParser(prog=name, description=description)

    parser.add_argument("--config",
                        default="./config.yml",
                        help="Path to the config file")

    if len(sys.argv) < 1:
        parser.print_help()
        sys.exit(0)

    return parser.parse_args(sys.argv[1:])
