import logging
import os
import traceback

from ..utils.logger import get_logger


class Lockfile:

    def __init__(self, path_to_lockfile: str):
        self.path = path_to_lockfile

    def __enter__(self):
        logging.info("Creating LogFile")
        with open(self.path, "w") as fp:
            try:
                fp.write("copying")
            except Exception:
                trace = traceback.format_stack()
                get_logger(__file__).error(trace)
                logging.error(
                    "Could not write to lockfile: {}".format(self.path))

    def __exit__(self, type, value, traceback):
        logging.info("Removing LogFile")
        try:
            os.remove(self.path)
        except Exception:
            trace = traceback.format_stack()
            get_logger(__file__).error(trace)
            logging.error("Could not remove lockfile: {}".format(self.path))


def create_lockfile(path_to_lockfile):
    return Lockfile(path_to_lockfile)
