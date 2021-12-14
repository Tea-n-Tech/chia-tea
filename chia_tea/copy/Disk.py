from dataclasses import dataclass
import glob
import ntpath
import os
import shutil
import time
import traceback
from typing import Dict, Set, Union

import psutil

from ..utils.logger import get_logger


def filter_least_used_disks(disk_to_copy_processes_count: Dict[str, int]) -> Set[str]:
    """Filters for the least used disk

    Parameters
    ----------
    disk_to_lockfile_count : Dict[str, int]
        Dictionary of disks with lockfile count

    Returns
    -------
    available_dirs : Set[str]
        Available directories with minimal lockfile count. In case of
        equal lockfile count then the disks are given randomly.
    """
    minimum_number_of_lockfiles = min(disk_to_copy_processes_count.values())
    available_target_dirpaths = {
        dirpath
        for dirpath in disk_to_copy_processes_count
        if disk_to_copy_processes_count[dirpath] == minimum_number_of_lockfiles
    }
    return available_target_dirpaths


def find_disk_with_space(
    filepath_file: str, target_dirs_process_count: Dict[str, int]
) -> Union[str, None]:
    """Searches for space for a file to be moved

    Parameters
    ----------
    filepath_file : str
        Path to the file to be copied
    target_dirs_process_count : Dict[str, int]
        Dictionary containing as key the directory and as value
        the number of copy processes for that directory.

    Returns
    -------
    dirpath : Union[str, None]
        A target dir with space or None if no space available
    """
    logger = get_logger(__file__)

    fstat = os.stat(filepath_file)

    # we collect multiple possible disks so that we can select one randomly
    # in the end.
    disks_with_space: Set[str] = set()

    for dirpath, n_processes in target_dirs_process_count.items():
        try:
            if not os.path.exists(dirpath):
                os.makedirs(dirpath, exist_ok=True)
            # size check
            space_after_copying = n_processes * 1.08e11  # 108GB
            space = psutil.disk_usage(dirpath)
            if space.free > (fstat.st_size + space_after_copying):
                disks_with_space.add(dirpath)
        except PermissionError:
            warn_msg = "Permission denied to directory '%s'."
            logger.warning(warn_msg, dirpath)
        except FileNotFoundError:
            warn_msg = "Directory '%s' does not exist."
            logger.warning(warn_msg, dirpath)
        except ConnectionResetError:
            warn_msg = "Lost connection to network drive '%s'"
            logger.warning(warn_msg, dirpath)
        except OSError:
            warn_msg = "Cannot reach host for drive '%s'"
            logger.warning(warn_msg, dirpath)

    if disks_with_space:
        return disks_with_space.pop()

    return None


def move_file(filepath, target_dir):
    """Moves a file to a target directory

    Parameters
    ----------
    filepath : str
        Path to the file to be moved
    target_dir : str
        Path to the target directory
    """
    logger = get_logger(__file__)

    if not os.path.isdir(target_dir):
        logger.error("Target directory '%s' does not exist.", target_dir)
        return

    # compose new filepath after move
    filename = ntpath.basename(filepath)
    target_path = os.path.join(target_dir, filename)

    # move file
    logger.info("moving file: %s -> %s", filepath, target_path)
    start = time.time()

    successful_copy = copy_file(filepath, target_path)

    duration_secs = time.time() - start
    if successful_copy:
        logger.info("copied '%s' in %.1fs", filepath, duration_secs)
        try:
            os.unlink(filepath)
        except FileNotFoundError:
            logger.error("Could not remove original file: %s", filepath)
    else:
        logger.error("failed to copy %s in %.1fs", filepath, duration_secs)


def copy_file(source_path: str, target_path: str) -> bool:
    """Copies a file from a source path to a target path

    Parameters
    ----------
    source_path : str
        Path to the existing source file
    target_path : str
        Path where to copy the file

    Returns
    -------
    success : bool
        If the copy was a success.
    """
    logger = get_logger(__file__)

    try:
        if is_accessible(source_path):
            shutil.copyfile(source_path, target_path)
            return True

        logger.error("Cannot copy file '%s' since it is being accessed.", source_path)
        return False

    except Exception:
        trace = traceback.format_stack()
        get_logger(__file__).error(trace)
        return False


def collect_files_from_folders(folder_set: Set[str], pattern: str) -> Set[str]:
    """Collect files from folders

    Parameters
    ----------
    folder_set : Set[str]
        set of folders to search for files
    pattern : str
        file pattern to search for

    Returns
    -------
    filepaths : Set[str]
        paths to the files
    """
    logger = get_logger(__file__)
    logger.debug("Collecting Plots")

    all_filepaths = set()

    for folder in folder_set:

        if not os.path.exists(folder):
            warn_msg = "Folder '%s' does not exist."
            logger.warning(warn_msg, folder)
            continue

        if os.path.isfile(folder):
            warn_msg = "Path '%s' is a file and not a directory."
            logger.warning(warn_msg, folder)
            continue

        if not os.path.isdir(folder):
            warn_msg = "Path '%s' is not a directory."
            logger.warning(warn_msg, folder)
            continue

        for filepath in glob.glob(os.path.join(folder, pattern)):
            if os.path.isfile(filepath):
                all_filepaths.add(filepath)

    return all_filepaths


def is_accessible(fpath: str) -> bool:
    """Looks if a file is accessible

    Parameters
    ----------
    fpath : str
        full path to the file

    Returns
    -------
    accessible : boolean
        false if being used by another process
    """

    logger = get_logger(__name__)
    try:
        with open(fpath, "r+", encoding="utf8"):
            pass
    except PermissionError:
        warn_msg = "File access check: Permission denied to file '%s'."
        logger.warning(warn_msg, os.path.abspath(fpath))
        return False
    except FileNotFoundError:
        warn_msg = "File access check: '%s' does not exist."
        logger.warning(warn_msg, os.path.abspath(fpath))
        return False
    except ConnectionResetError:
        warn_msg = "File access check: Lost connection to network on file: '%s'"
        logger.warning(warn_msg, os.path.abspath(fpath))
        return False
    except OSError:
        warn_msg = "File access check: Cannot reach file '%s'"
        logger.warning(warn_msg, os.path.abspath(fpath))
        return False

    return True


@dataclass
class DiskCopyInfo:
    """Information which files in the folder are being copied and which not"""

    files_in_progress: Set[str]
    files_not_being_copied: Set[str]


def get_files_being_copied(directories: Set[str]) -> Dict[str, DiskCopyInfo]:
    """Get all the files which are not accessible for write (i.e. being copied)

    Parameters
    ----------
    directories : Set[str]
        Directories where to search for files, which cannot be accessed (i.e. being copied)
    previous_check : Dict[str, DiskCopyInfo]
        Dictionary containing as key the directory and as value the disk copy
        info from the previous check to speed up the check. Previous files not
        being copied are not checked again.

    Returns
    -------
    disk_copy_data : Dict[str, DiskCopyInfo]
        Dictionary containing as key the directory and as value the disk copy
        info.
    """
    disk_copy_data: Dict[str, DiskCopyInfo] = {}

    logger = get_logger(__file__)
    for folder_path in directories:

        new_info = DiskCopyInfo(files_in_progress=set(), files_not_being_copied=set())

        if not os.path.exists(folder_path):
            logger.warning("Target directory '%s' does not exist.", folder_path)
            continue

        if not os.path.isdir(folder_path):
            logger.warning("Target directory '%s' is not a directory.", folder_path)
            continue

        disk_copy_data[folder_path] = new_info

        all_files_to_check = {
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        }

        for f in all_files_to_check:
            if not is_accessible(f):
                new_info.files_in_progress.add(f)
            else:
                new_info.files_not_being_copied.add(f)

    return disk_copy_data
