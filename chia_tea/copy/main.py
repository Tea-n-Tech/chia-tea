import time
import traceback
from typing import Dict

from ..protobuf.generated.config_pb2 import ChiaTeaConfig
from ..utils.logger import get_logger
from .Disk import (
    collect_files_from_folders,
    filter_least_used_disks,
    find_disk_with_space,
    get_files_being_copied,
    move_file,
)


def run_copy(config: ChiaTeaConfig) -> None:
    """Run an infinite copy loop copying files

    Parameters
    ----------
    config : ChiaTeaConfig
        Config containing the copy settings
    """

    # get logger
    logger = get_logger(__file__)

    from_folders = set(config.copy.source_folders)
    target_folders = set(config.copy.target_folders)

    logger.info("Copying from: %s", from_folders)
    logger.info("Copying to  : %s", target_folders)

    # execute infinite copy loop
    while True:
        iteration_start_time = time.time()
        try:
            files_to_copy = collect_files_from_folders(from_folders, "*.plot")

            # pick a file
            source_filepath = files_to_copy.pop()

            # Check which files are being copied. This helps us to select a
            # disk which is used the least.
            disk_copy_data = get_files_being_copied(directories=target_folders)

            disk_to_copy_processes_count: Dict[str, int] = {
                folder: len(data.files_in_progress) for folder, data in disk_copy_data.items()
            }

            # check if we have enough space on the disks of the target folders
            available_target_dirpaths = filter_least_used_disks(disk_to_copy_processes_count)

            # filter out the folders which are available
            disk_to_copy_processes_count = {
                disk: disk_to_copy_processes_count[disk] for disk in available_target_dirpaths
            }

            # search for a space on the specified disks
            target_dir = find_disk_with_space(source_filepath, disk_to_copy_processes_count)
            if target_dir is None:
                raise RuntimeError("No disk space available for: %s" % source_filepath)

            # compose new filepath after move
            move_file(source_filepath, target_dir)

        except Exception as err:
            trace = traceback.format_stack()
            logger.error("%s", err)
            logger.debug(trace)

        finally:
            # if the iteration took less than the specified interval, wait
            # this is to prevent the loop from running too fast
            duration_secs = time.time() - iteration_start_time
            sleep_time_secs = 15 - min(duration_secs, 15)
            time.sleep(sleep_time_secs)
