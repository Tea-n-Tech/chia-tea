import unittest
from unittest.mock import patch, MagicMock, Mock

from .Disk import (
    collect_files_from_folders,
    filter_least_used_disks,
    find_disk_with_space,
    is_accessible,
    update_completely_copied_files,
)


# we need to mock the join function with our own implementation
# because the original one will be mocked by the unittest
def _path_join(*args):
    return "/".join(args)


class TestDisk(unittest.TestCase):
    def test_filter_least_used_disks_works(self):
        result = filter_least_used_disks(
            {
                "a": 1,
                "b": 2,
                "c": 3,
                "d": 1,
            }
        )
        self.assertSetEqual(result, {"a", "d"})

    @patch("chia_tea.copy.Disk.os.path")
    @patch("chia_tea.copy.Disk.is_accessible")
    @patch("chia_tea.copy.Disk.os")
    def test_update_completely_copied_files(self, os_mock, is_accessible_mock, path_mock):

        files_not_folders = [
            "some_file",
        ]
        not_existing_folders = [
            "not_existing_folder",
        ]
        files_in_folders = {
            "folder_a": [
                "file_a",
                "file_b",
            ],
        }
        existing_files_and_folders = list(files_in_folders.keys()) + files_not_folders

        def _listdir_mock(path):
            if path in files_in_folders:
                return files_in_folders[path]
            return []

        all_folders_and_files = existing_files_and_folders + not_existing_folders

        os_mock.listdir = _listdir_mock
        path_mock.join = _path_join
        # pretend the first folder doesn't exist
        path_mock.exists = lambda name: name in existing_files_and_folders
        # and the second folder is a file
        path_mock.isdir = lambda name: name in files_in_folders
        path_mock.isfile.return_value = True
        is_accessible_mock.return_value = True

        files_copied_completely = {"folder_a/file_a"}
        output = update_completely_copied_files(all_folders_and_files, files_copied_completely)

        self.assertSetEqual(output, {"folder_a/file_a", "folder_a/file_b"})

    @patch("chia_tea.copy.Disk.os.path")
    @patch("chia_tea.copy.Disk.glob")
    def test_collect_files_from_folders(self, glob_mock, path_mock):
        files_in_folders = {
            "folder_a": [
                "folder_a/file_a",
                "folder_a/file_b",
                "folder_a/subfolder",
            ],
        }

        not_existing_folders = {"not_existing_folder"}
        files_and_not_folders = {"some_file"}
        some_symlink = {"some_symlink"}
        all_directory_items = (
            *set(files_in_folders.keys()),
            *not_existing_folders,
            *files_and_not_folders,
            *some_symlink,
        )

        expected_filepaths = {
            "folder_a/file_a",
            "folder_a/file_b",
        }

        glob_mock.glob = lambda _: files_in_folders["folder_a"]
        path_mock.exists = lambda path: path != "not_existing_folder"
        path_mock.isfile = lambda path: path in {
            "folder_a/file_a",
            "folder_a/file_b",
            "some_file",
        }
        path_mock.isdir = lambda path: path in {"folder_a", "folder_a/subfolder"}
        path_mock.join = _path_join

        filepath_set = collect_files_from_folders(
            folder_set=all_directory_items,
            pattern="*",
        )
        self.assertSetEqual(filepath_set, expected_filepaths)

    @patch("chia_tea.copy.Disk.open")
    def test_is_accessible(self, open_mock: MagicMock):

        filepath = "some/file/path"

        # is accessible
        result = is_accessible(filepath)
        self.assertTrue(result)
        open_mock.assert_called_with(filepath, "r+", encoding="utf8")

        # permission error
        open_mock.reset_mock()
        open_mock.side_effect = PermissionError()
        result = is_accessible(filepath)
        self.assertFalse(result)
        open_mock.assert_called_with(filepath, "r+", encoding="utf8")

        # file not found
        open_mock.reset_mock()
        open_mock.side_effect = FileNotFoundError()
        result = is_accessible(filepath)
        self.assertFalse(result)
        open_mock.assert_called_with(filepath, "r+", encoding="utf8")

        # connection error to network drive
        open_mock.reset_mock()
        open_mock.side_effect = ConnectionResetError()
        result = is_accessible(filepath)
        self.assertFalse(result)
        open_mock.assert_called_with(filepath, "r+", encoding="utf8")

        # file not reachable
        open_mock.reset_mock()
        open_mock.side_effect = OSError()
        result = is_accessible(filepath)
        self.assertFalse(result)
        open_mock.assert_called_with(filepath, "r+", encoding="utf8")

    @patch("chia_tea.copy.Disk.psutil")
    @patch("chia_tea.copy.Disk.filter_least_used_disks")
    @patch("chia_tea.copy.Disk.update_copy_processes_count")
    @patch("chia_tea.copy.Disk.os.path")
    @patch("chia_tea.copy.Disk.os")
    def test_find_disk_with_space(
        self,
        os_mock,
        path_mock,
        update_copy_processes_count_mock,
        filter_least_used_disks_mock,
        psutil_mock,
    ):
        # pylint: disable=too-many-arguments

        file_to_copy = "path/to/file"
        target_folders = {
            "folder_a",
        }

        os_mock.stat.return_value = Mock(st_size=1.08e11)
        update_copy_processes_count_mock.return_value = {folder: 1 for folder in target_folders}
        filter_least_used_disks_mock.return_value = target_folders
        # path_mock.exists = lambda path: path != "folder_which_doesnt_exist_yet"
        path_mock.exists.return_value = True
        psutil_mock.disk_usage.return_value = Mock(free=3 * 1.08e11)

        result = find_disk_with_space(
            target_dirs=target_folders, filepath_file=file_to_copy, copied_files={}
        )
        self.assertEqual(result, "folder_a")
        os_mock.makedirs.assert_not_called()
        os_mock.stat.assert_called_with(file_to_copy)
        filter_least_used_disks_mock.assert_called_once()
        update_copy_processes_count_mock.assert_called_once()
        path_mock.exists.assert_called_once()
        psutil_mock.disk_usage.assert_called_with("folder_a")
