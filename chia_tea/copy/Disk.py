import os
import glob
import shutil
import traceback
from typing import Dict, Set, Tuple, Union

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


def update_completely_copied_files(
    target_dirs: Set[str], previously_copied_files: Set[str]
) -> Set[str]:
    """For each target dir, it will add the completly copied files

    Parameters
    ----------
    target_dirs : Set[str]
        Directories in which the file can be copied
    previously_copied_files : Set[str]
        All the files which are not being copied anymore.
        If specified these files will not be checked since
        we assume they are done once copied.

    Returns
    -------
    previously_copied_files: Set[str]
        All the files which are not being copied anymore
    """
    logger = get_logger(__file__)
    logger.debug("Updating copied files")

    # make a copy to avoid manipulating the input set
    copied_files = set(previously_copied_files)

    for folder_path in target_dirs:

        if not os.path.exists(folder_path):
            logger.warning("Target directory '%s' does not exist.", folder_path)
            continue

        if not os.path.isdir(folder_path):
            logger.warning("Target directory '%s' is not a directory.", folder_path)
            continue

        all_files = {
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        }

        for f in all_files:
            if f not in copied_files:
                if is_accessible(f):
                    copied_files.add(f)

    return copied_files


def find_disk_with_space(
    target_dirs: Set[str], filepath_file: str, copied_files: Set[str]
) -> Union[str, None]:
    """Searches for space for a file to be moved

    Parameters
    ----------
    target_dirs : Set[str]
        Directories in which the file can be copied
    filepath_file : str
        Path to the file to be copied
    copied_files : Set[str]
        All the files which are not being copied anymore

    Returns
    -------
    dirpath : Union[str, None]
        A target dir with space or None if no space available
    """
    logger = get_logger(__file__)

    fstat = os.stat(filepath_file)
    disk_to_copy_processes_count = update_copy_processes_count(target_dirs, copied_files)
    available_target_dirpaths = filter_least_used_disks(disk_to_copy_processes_count)

    for dirpath in available_target_dirpaths:
        try:
            if not os.path.exists(dirpath):
                os.makedirs(dirpath, exist_ok=True)
            # size check
            n_processes = disk_to_copy_processes_count[dirpath]
            space_after_copying = n_processes * 1.08e11  # 108GB
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


def update_copy_processes_count(target_dirs: Set[str], files_copied_completely) -> Dict[str, int]:
    """Get the copy processes count for the specified directories

    Parameters
    ----------
    target_dirs : Set[str]
        Directories to get copy processes count for.

    Returns
    -------
    number_of_copy_processes_per_disk : Dict[str, int]
        Dictionary containing as key the directory and as
        value den copy processes count.
    """
    number_of_copy_processes_per_disk = {}

    for target_dir in target_dirs:
        files_beeing_copied_to_dir = get_files_being_copied([target_dir], files_copied_completely)
        number_of_copy_processes = len(files_beeing_copied_to_dir)
        number_of_copy_processes_per_disk[target_dir] = number_of_copy_processes

    return number_of_copy_processes_per_disk


def get_files_being_copied(
    directories: Set[str], previously_checked_files: Set[str]
) -> Tuple[Set[str], Set[str]]:
    """Get all the files which are not accessible for write (i.e. being copied)

    Parameters
    ----------
    directories : Set[str]
        Directories where to search for files, which cannot be accessed (i.e. being copied)

    previously_checked_files : Set[str]
        Already known files which are accessed right now
        Those files are not checked. Update of that Set happens separately

    Returns
    -------
    files_in_progress : Set[str]
        Set with all the files, which are being denied accesse (i.e. being copied)
    files_not_being_copied : Set[str]
        All files which are not being copied
    """
    files_in_progress = set()
    files_not_being_copied = set(previously_checked_files)

    logger = get_logger(__file__)
    for folder_path in directories:

        if not os.path.isdir(folder_path):
            if os.path.isfile(folder_path):
                warn_msg = "Path '%s' is a file and not a directory."
            else:
                warn_msg = "Folder '%s' does not exist or is not a directory."
            logger.warning(warn_msg, folder_path)
            continue

        all_files_to_check = {
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        }

        all_files_to_check.difference_update(files_not_being_copied)

        # check
        for f in all_files_to_check:
            if not is_accessible(f):
                files_in_progress.add(f)
            else:
                files_not_being_copied.add(f)

    return files_in_progress, files_not_being_copied
