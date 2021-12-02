import ntpath
import os
import time

from ..protobuf.generated.config_pb2 import ChiaTeaConfig
from ..utils.logger import get_logger
from .Disk import (
    collect_files_from_folders,
    copy_file,
    find_disk_with_space,
    update_completely_copied_files,
)


def run_copy(config: ChiaTeaConfig) -> None:
    """Run an infinite copy loop copying files

    Parameters
    ----------
    filepath : str
        The filepath to the config file
    """

    # get logger
    logger = get_logger(__file__)

    # little hack since "from" is a reserved keyword in python
    from_folders = set(config.copy.source_folders)
    target_folders = set(config.copy.target_folders)

    logger.info("Copying from: %s", from_folders)
    logger.info("Copying to  : %s", target_folders)

    # execute infinite copy loop
    while True:
        print("collecting Plots")
        files_to_copy = collect_files_from_folders(from_folders, "*.plot")

        print("Updating copiedFiles")
        files_copied_completely = update_completely_copied_files(
            target_folders, files_copied_completely
        )

        for source_filepath in files_to_copy:
            print("copy process")
            # search for a space on the specified disks
            target_dir = find_disk_with_space(
                target_folders, source_filepath, files_copied_completely
            )
            if target_dir is None:
                logger.error("No disk space available for: %s", source_filepath)
                continue

            # compose new filepath after move
            filename = ntpath.basename(source_filepath)
            target_path = os.path.join(target_dir, filename)

            # move file (with measurement)
            logger.info("moving file: %s -> %s", source_filepath, target_path)
            start = time.time()

            successful_copy = copy_file(source_filepath, target_path)

            duration_secs = time.time() - start
            if successful_copy:
                logger.info("done in %.1fs", duration_secs)
                try:
                    os.remove(source_filepath)
                except FileNotFoundError:
                    logger.error("Could not remove original file: %s", source_filepath)

            else:
                logger.error("failed to copy %s in %.1fs", source_filepath, duration_secs)

        # rate limiter
        time.sleep(15)
