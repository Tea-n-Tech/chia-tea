import os
import glob
import random
import shutil
import time
import traceback
from os.path import isfile, join
from typing import Dict, List, Union

import psutil

from ..utils.logger import get_logger


def filter_least_used_disks(disk_to_copy_processes_count: Dict[str, int]) -> List[str]:
    """Filters for the least used disk

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
    minimum_number_of_lockfiles = min(disk_to_copy_processes_count.values())
    available_target_dirpaths = [
        dirpath
        for dirpath in disk_to_copy_processes_count
        if disk_to_copy_processes_count[dirpath] == minimum_number_of_lockfiles
    ]
    random.shuffle(available_target_dirpaths)
    return available_target_dirpaths


def update_completely_copied_files(target_dirs: List[str], files_copied_completely: List[str]) -> List[str]:
    """ For each target dir, it will add the completly copied files
    Parameters
    ----------
    target_dirs: List[str]
        Directories in which the file can be copied

    Returns
    -------
    files_copied_completely: List[str]
        All the files which are not being copied anymore
    """
    logger = get_logger(__file__)
    for folder_path in target_dirs:

        if not os.path.isdir(folder_path):
            if os.path.isfile(folder_path):
                warn_msg = "Path '{0}' is a file and not a directory."
            else:
                warn_msg = "Folder '{0}' does not exist or is not a directory."
            logger.warning(warn_msg, folder_path)
            continue

        all_files = [f for f in os.listdir(
            folder_path) if isfile(join(folder_path, f))]
        for f in all_files:
            if f not in files_copied_completely:
                if not is_being_used(f):
                    files_copied_completely.append(f)
    return files_copied_completely


def find_disk_with_space(target_dirs: List[str], filepath_file: str, files_copied_completely: List[str]) -> Union[str, None]:
    """Searches for space for a file to be moved

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
    disk_to_copy_processes_count = update_copy_processes_count(
        target_dirs, files_copied_completely)
    available_target_dirpaths = filter_least_used_disks(
        disk_to_copy_processes_count)

    for dirpath in available_target_dirpaths:
        try:
            if not os.path.isdir(dirpath):
                os.makedirs(dirpath, exist_ok=True)
            # size check
            n_lockfiles = disk_to_copy_processes_count[dirpath]
            space_after_copying = n_lockfiles * 1.08e11  # 108GB
            space = psutil.disk_usage(dirpath)
            if space.free > (fstat.st_size + space_after_copying):
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
    """Copies a file from a source path to a target path

    Parameters
    ----------
    source_path: str
        Path to the existing source file
    target_path: str
        Path where to copy the file

    Returns
    -------
    success: bool
        If the copy was a success.
    """
    print(target_path)
    with open(source_path, "rb") as fin:
        with open(target_path, "wb") as fout:
            try:
                shutil.copyfileobj(fin, fout, 128 * 1024)
            except (Exception, ConnectionResetError):
                trace = traceback.format_stack()
                get_logger(__file__).error(trace)
                return False
    return True


def collect_files_from_folders(folder_list: List[str], pattern: str) -> List[str]:
    """Collect files from folders

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


def is_being_used(fpath):
    """Looks if a file is being used on from a different process
    Parameters
    ----------
    fpath: str
        full(!) path to the file

    Returns
    -------
    being_used: boolean
        true if being used by another process
    """
    for proc in psutil.process_iter():
        try:
            for item in proc.open_files():
                if fpath == item.path:
                    return True
        except Exception:
            pass

    return False


def is_accessible(fpath):
    """Looks if a file is being accessible
    Parameters
    ----------
    fpath: str
        full(!) path to the file

    Returns
    -------
    accessible: boolean
        false if being used by another process
    """
    print(fpath)
    try:
        start = time.time()
        for i in range(1, 1000):
            with open(fpath, "r+"):
                pass
        end = time.time()
        print(end - start)
    except Exception:
        return False
    return True


def update_copy_processes_count(target_dirs: List[str], files_copied_completely) -> Dict[str, int]:
    """Get the copy processes count for the specified directories

    Parameters
    ----------
    target_dirs: List[str]
        Directories to get copy processes count for.

    Returns
    -------
    number_of_copy_processes_per_disk: Dict[str, int]
        Dictionary containing as key the directory and as
        value den copy processes count.
    """
    print("Updating Copy Process Counts")
    number_of_copy_processes_per_disk = {}
    for target_dir in target_dirs:
        files_beeing_copied_to_dir = get_files_beingCopied(
            [target_dir], files_copied_completely)
        number_of_copy_processes = len(files_beeing_copied_to_dir)
        print("Number of copy processes:  {}".format(number_of_copy_processes))
        print("Number of complete copied processes:  {}".format(
            len(files_copied_completely)))
        number_of_copy_processes_per_disk[target_dir] = number_of_copy_processes
    return number_of_copy_processes_per_disk


def get_files_beingCopied(target_dirs: List[str], files_copied_completely: List[str]) -> List[str]:
    """
    Later
    """
    all_filepaths = []
    logger = get_logger(__file__)
    for folder_path in target_dirs:

        if not os.path.isdir(folder_path):
            if os.path.isfile(folder_path):
                warn_msg = "Path '{0}' is a file and not a directory."
            else:
                warn_msg = "Folder '{0}' does not exist or is not a directory."
            logger.warning(warn_msg, folder_path)
            continue

        all_files_to_check = [f for f in os.listdir(
            folder_path) if isfile(join(folder_path, f))]

        all_files_to_check = [f for f in os.listdir(
            folder_path) if isfile(join(folder_path, f))]

        # remove all files which not have to be cheked
        print(files_copied_completely)
        for f in files_copied_completely:
            if f in all_files_to_check:
                all_files_to_check.remove(f)
                print("Removed: "+f + " as it is already copied completely")

        # check
        for f in all_files_to_check:
            if is_being_used(f):
                print("!!!!!!!! File {} is being used".format(f))
                all_filepaths.append(f)
            else:
                files_copied_completely.append(f)
                print("Added "+f +
                      " because it is already copied completely")

        return all_filepaths
