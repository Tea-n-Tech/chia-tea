import ntpath
import os
import time

from ..utils.cli import parse_args
from ..utils.config import read_config
from ..utils.logger import get_logger
from .Disk import collect_files_from_folders, copy_file, find_disk_with_space
from .Lockfile import create_lockfile

module_name = "chia_tea.copy"


def main():
    """ Main program for copying files
    """

    # get command line arguments
    args = parse_args(
        name="Chia Tea Copy",
        description="Start a process copying files for your chia farm."
    )

    # load config
    config = read_config(args.config)

    # get logger
    logger = get_logger(module_name)

    # little hack since "from" is a reserved keyword in python
    from_folders = config.copy.source_folders
    target_folders = config.copy.target_folders

    logger.info("Copying from: %s", from_folders)
    logger.info("Copying to  : %s", target_folders)

    # execute infinite copy loop
    while True:

        files_to_copy = collect_files_from_folders(from_folders, "*.plot")

        for filepath in files_to_copy:
            # search for a space on the specified disks
            target_dir = find_disk_with_space(target_folders, filepath)
            if target_dir is None:
                logger.error("No disk space available for: %s", filepath)
                continue

            # compose new filepath after move
            filename = ntpath.basename(filepath)
            target_path = os.path.join(target_dir, filename)

            # move file (with measurement)
            logger.info(
                "moving file: %s -> %s", filepath, target_path)
            start = time.time()

            # lockfile
            path_to_lockfile = os.path.join(
                target_dir, filename.replace(".plot", ".copying"))

            with create_lockfile(path_to_lockfile):
                successful_copy = copy_file(filepath, target_path)

            duration_secs = time.time() - start
            if successful_copy:
                logger.info("done in %.1fs", duration_secs)
                try:
                    os.remove(filepath)
                except FileNotFoundError:
                    logger.error(
                        "Could not remove original file: %s", filepath)

            else:
                logger.error("failed to copy %s in %.1fs",
                             filepath, duration_secs)

        # rate limiter
        time.sleep(15)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        get_logger(module_name).info("Shutting down.")
