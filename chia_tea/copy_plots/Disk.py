import glob
import os
import random
import shutil
import traceback
from typing import Dict, List, Union

import psutil

from ..utils.logger import get_logger


def filter_least_used_disks(disk_to_lockfile_count: Dict[str, int]) -> List[str]:
    """ Filters for the least used disk

    Parameters
    ----------
    disk_to_lockfile_count : Dict[str, int]
        Dictionary of disks with lockfile count

    Returns
    -------
    available_dirs : List[str]
        Available directories with minimal lockfile count. In case of
        equal lockfile count then the disks are given randomly.
    """
    minimum_number_of_lockfiles = min(disk_to_lockfile_count.values())
    available_target_dirpaths = [
        dirpath for dirpath in disk_to_lockfile_count
        if disk_to_lockfile_count[dirpath] == minimum_number_of_lockfiles]
    random.shuffle(available_target_dirpaths)
    return available_target_dirpaths


def find_disk_with_space(target_dirs: List[str],
                         filepath_file: str) -> Union[str, None]:
    """ Searches for space for a file to be moved

    Parameters
    ----------
    target_dirs: List[str]
        Directories in which the file can be copied
    filepath_file: str
        Path to the file to be copied

    Returns
    -------
    dirpath: Union[str, None]
        A target dir with space or None if no space available
    """
    logger = get_logger(__file__)
    fstat = os.stat(filepath_file)
    disk_to_lockfile_count = update_lockfile_count(target_dirs)
    available_target_dirpaths = filter_least_used_disks(disk_to_lockfile_count)

    for dirpath in available_target_dirpaths:
        try:
            if not os.path.isdir(dirpath):
                os.makedirs(dirpath, exist_ok=True)
            # size check
            n_lockfiles = disk_to_lockfile_count[dirpath]
            space_after_copying = n_lockfiles*1.08e+11  # 108GB
            space = psutil.disk_usage(dirpath)
            if space.free > (fstat.st_size+space_after_copying):
                return dirpath
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

    return None


def copy_file(source_path: str, target_path: str) -> bool:
    """ Copies a file from a source path to a target path

    Parameters
    ----------
    source_path : str
        Path to the existing source file
    target_path: str
        Path where to copy the file

    Returns
    -------
    success : bool
        If the copy was a success.
    """
    print(target_path)
    with open(source_path, 'rb') as fin:
        with open(target_path, 'wb') as fout:
            try:
                shutil.copyfileobj(fin, fout, 128*1024)
            except (Exception, ConnectionResetError):
                trace = traceback.format_stack()
                get_logger(__file__).error(trace)
                return False
    return True


def collect_files_from_folders(folder_list: List[str],
                               pattern: str) -> List[str]:
    """ Collect files from folders

    Parameters
    ----------
    folder_list : List[str]
        list of folders to search for files
    pattern : str
        file pattern to search for

    Returns
    -------
    filepaths : List[str]
        paths to the files
    """
    logger = get_logger(__file__)

    all_filepaths = []

    for folder_path in folder_list:

        if not os.path.isdir(folder_path):
            if os.path.isfile(folder_path):
                warn_msg = "Path '{0}' is a file and not a directory."
            else:
                warn_msg = "Folder '{0}' does not exist or is not a directory."
            logger.warning(warn_msg, folder_path)
            continue

        all_filepaths += glob.glob(os.path.join(folder_path, pattern))

    return all_filepaths


def update_lockfile_count(target_dirs: List[str]) -> Dict[str, int]:
    """ Get the lockfile count for the specified directories

    Parameters
    ----------
    target_dirs : List[str]
        Directories to get lockfile count for.

    Returns
    -------
    lockfile_count : Dict[str, int]
        Dictionary containing as key the directory and as
        value den lockfile count.
    """
    n_lockfiles_per_disk = {}
    for target_dir in target_dirs:
        lock_files = collect_files_from_folders([target_dir], "*.copying")
        n_lockfiles = len(lock_files)
        n_lockfiles_per_disk[target_dir] = n_lockfiles
    return n_lockfiles_per_disk
