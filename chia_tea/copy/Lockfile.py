import logging
import os
import traceback

from ..utils.logger import get_logger


class Lockfile:
    """Class to manage lockfiles"""

    def __init__(self, path_to_lockfile: str):
        self.path = path_to_lockfile

    def __enter__(self):
        logging.info("Creating Lockfile: %s", self.path)
        with open(self.path, "w", encoding="utf8") as fp:
            try:
                fp.write("copying")
            except Exception:
                logger = get_logger(__file__)
                logger.error("Could not write to lockfile: %s", self.path)
                logger.error(traceback.format_stack())

    def __exit__(self, exception_type, exception_value, exception_traceback):
        logging.info("Removing LogFile")
        try:
            os.remove(self.path)
        except Exception:
            logger = get_logger(__file__)
            logger.error("Could not remove lockfile: %s", self.path)
            logger.error(exception_traceback.format_stack())


def create_lockfile(path_to_lockfile: str) -> Lockfile:
    """Creates a lockfile if used in a context through 'with'

    Parameters
    ----------
    path_to_lockfile : str
        filepath of lockfile

    Returns
    -------
    lockfile : Lockfile
        Lockfile instance which creates a lockfile if used in
        combination with a 'with' statement.
    """
    return Lockfile(path_to_lockfile)
