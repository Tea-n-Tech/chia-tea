import ntpath
import unittest
from unittest.mock import call, patch, MagicMock, Mock

from .Disk import (
    DiskCopyInfo,
    collect_files_from_folders,
    copy_file,
    filter_least_used_disks,
    find_disk_with_space,
    get_files_being_copied,
    is_accessible,
    move_file,
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
            *files_in_folders.keys(),
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
    @patch("chia_tea.copy.Disk.os.path")
    @patch("chia_tea.copy.Disk.os")
    def test_find_disk_with_space(
        self,
        os_mock: MagicMock,
        path_mock: MagicMock,
        psutil_mock: MagicMock,
    ):
        file_to_copy = "path/to/file"
        target_dirs_process_count = {
            "folder_a": 1,
            "folder_b": 2,
        }

        os_mock.stat.return_value = Mock(st_size=1.08e11)
        path_mock.exists.return_value = True
        psutil_mock.disk_usage.return_value = Mock(free=3 * 1.08e11)

        result = find_disk_with_space(
            filepath_file=file_to_copy,
            target_dirs_process_count=target_dirs_process_count,
        )
        self.assertEqual(result, "folder_a")
        os_mock.makedirs.assert_not_called()
        os_mock.stat.assert_called_with(file_to_copy)
        path_mock.exists.assert_has_calls(
            [call(folder) for folder in target_dirs_process_count],
            any_order=True,
        )
        psutil_mock.disk_usage.assert_has_calls(
            [call(folder) for folder in target_dirs_process_count],
            any_order=True,
        )

        # different error handling
        for err in (
            PermissionError(),
            FileNotFoundError(),
            ConnectionResetError(),
            OSError(),
        ):
            os_mock.reset_mock()
            path_mock.reset_mock()
            psutil_mock.reset_mock()

            os_mock.stat.return_value = Mock(st_size=1.08e11)
            os_mock.path.exists.side_effect = err

            result = find_disk_with_space(
                filepath_file=file_to_copy,
                target_dirs_process_count=target_dirs_process_count,
            )
            self.assertIsNone(result)
            os_mock.stat.assert_called_with(file_to_copy)
            path_mock.exists.assert_has_calls(
                [call(folder) for folder in target_dirs_process_count],
                any_order=True,
            )

    @patch("chia_tea.copy.Disk.shutil.copyfile")
    @patch("chia_tea.copy.Disk.is_accessible")
    def test_copy_file(self, is_accessible_mock, copyfile_mock):

        source_file = "source_file"
        target_file = "target_file"

        # success case
        is_accessible_mock.return_value = True
        success = copy_file(source_file, target_file)
        self.assertTrue(success)
        is_accessible_mock.assert_called_once_with(source_file)
        copyfile_mock.assert_called_once_with(source_file, target_file)

        is_accessible_mock.reset_mock()
        copyfile_mock.reset_mock()

        # not accessible case
        is_accessible_mock.return_value = False
        success = copy_file(source_file, target_file)
        self.assertFalse(success)
        is_accessible_mock.assert_called_once_with(source_file)
        copyfile_mock.assert_not_called()

        is_accessible_mock.reset_mock()
        copyfile_mock.reset_mock()

        # unexpected exception during anything
        is_accessible_mock.side_effect = Exception()
        success = copy_file(source_file, target_file)
        self.assertFalse(success)
        is_accessible_mock.assert_called_once_with(source_file)
        copyfile_mock.assert_not_called()

        is_accessible_mock.reset_mock()
        copyfile_mock.reset_mock()

    @patch("chia_tea.copy.Disk.os.path")
    def test_move_file_target_is_not_dir(self, path_mock):

        # pylint: disable=no-self-use

        source_file = "source_file"
        target_folder = "folder"

        path_mock.isdir.return_value = False

        move_file(source_file, target_folder)
        path_mock.isdir.assert_called_once_with(target_folder)

    @patch("chia_tea.copy.Disk.os.path")
    @patch("chia_tea.copy.Disk.copy_file")
    @patch("chia_tea.copy.Disk.os")
    def test_move_file_all_ok(self, os_mock, copy_file_mock, path_mock):

        # pylint: disable=no-self-use

        source_file = "source_file"
        target_folder = "folder"
        filename = ntpath.basename(source_file)
        target_path = _path_join(target_folder, filename)

        path_mock.join = _path_join
        path_mock.isdir.return_value = True
        copy_file_mock.return_value = True

        move_file(source_file, target_folder)

        path_mock.isdir.assert_called_once_with(target_folder)
        copy_file_mock.assert_called_once_with(source_file, target_path)
        os_mock.unlink.assert_called_once_with(source_file)

    @patch("chia_tea.copy.Disk.os.path")
    @patch("chia_tea.copy.Disk.copy_file")
    @patch("chia_tea.copy.Disk.os")
    def test_move_file_unsuccessful_copy(self, os_mock, copy_file_mock, path_mock):

        # pylint: disable=no-self-use

        source_file = "source_file"
        target_folder = "folder"
        filename = ntpath.basename(source_file)
        target_path = _path_join(target_folder, filename)

        path_mock.join = _path_join
        path_mock.isdir.return_value = True
        copy_file_mock.return_value = False

        move_file(source_file, target_folder)

        path_mock.isdir.assert_called_once_with(target_folder)
        copy_file_mock.assert_called_once_with(source_file, target_path)
        os_mock.unlink.assert_not_called()

    @patch("chia_tea.copy.Disk.os.path")
    @patch("chia_tea.copy.Disk.copy_file")
    @patch("chia_tea.copy.Disk.os")
    def test_move_file_cannot_unlink_original(self, os_mock, copy_file_mock, path_mock):

        # pylint: disable=no-self-use

        source_file = "source_file"
        target_folder = "folder"
        filename = ntpath.basename(source_file)
        target_path = _path_join(target_folder, filename)

        path_mock.join = _path_join
        path_mock.isdir.return_value = True
        copy_file_mock.return_value = True
        os_mock.unlink.side_effect = FileNotFoundError()

        move_file(source_file, target_folder)

        path_mock.isdir.assert_called_once_with(target_folder)
        copy_file_mock.assert_called_once_with(source_file, target_path)
        os_mock.unlink.assert_called_once_with(source_file)

    @patch("chia_tea.copy.Disk.is_accessible")
    @patch("chia_tea.copy.Disk.os.path")
    @patch("chia_tea.copy.Disk.os")
    def test_get_files_being_copied_with_no_prev_checked_files(
        self, os_mock, path_mock, is_accessible_mock
    ):

        target_dirs = {
            "folder_a",
        }
        expected_result = {
            "folder_a": DiskCopyInfo(
                files_in_progress=set(),
                files_not_being_copied={
                    "folder_a/file_copied",
                },
            ),
        }

        # mock stuff
        os_mock.listdir.return_value = ["file_copied"]
        path_mock.join = _path_join
        path_mock.exists.return_value = True
        path_mock.isdir.return_value = True
        path_mock.isfile.return_value = True
        is_accessible_mock.return_value = True

        # do the thing
        result = get_files_being_copied(directories=target_dirs)

        # checks
        for folder, info in result.items():
            self.assertSetEqual(
                info.files_in_progress,
                expected_result[folder].files_in_progress,
            )
            self.assertSetEqual(
                info.files_not_being_copied,
                expected_result[folder].files_not_being_copied,
            )

        is_accessible_mock.assert_has_calls(
            [
                *(
                    call(path)
                    for info in expected_result.values()
                    for path in info.files_not_being_copied
                ),
                *(
                    call(path)
                    for info in expected_result.values()
                    for path in info.files_in_progress
                ),
            ],
            any_order=True,
        )
        os_mock.listdir.assert_has_calls(
            [call(dirname) for dirname in target_dirs],
            any_order=True,
        )

    @patch("chia_tea.copy.Disk.is_accessible")
    @patch("chia_tea.copy.Disk.os.path")
    @patch("chia_tea.copy.Disk.os")
    def test_get_files_being_copied_with_copies_in_progress(
        self, os_mock, path_mock, is_accessible_mock
    ):

        target_dirs = {
            "folder_a",
            "folder_b",
        }
        expected_result = {
            "folder_a": DiskCopyInfo(
                files_in_progress={
                    "folder_a/file_in_progress",
                },
                files_not_being_copied=set(),
            ),
            "folder_b": DiskCopyInfo(
                files_in_progress={
                    "folder_b/file_in_progress",
                },
                files_not_being_copied=set(),
            ),
        }

        # mock stuff
        os_mock.listdir.return_value = ["file_in_progress"]
        path_mock.join = _path_join
        path_mock.exists.return_value = True
        path_mock.isdir.return_value = True
        path_mock.isfile.return_value = True
        is_accessible_mock.return_value = False

        # do the thing
        result = get_files_being_copied(directories=target_dirs)

        # checks
        for folder, info in result.items():
            self.assertSetEqual(
                info.files_in_progress,
                expected_result[folder].files_in_progress,
            )
            self.assertSetEqual(
                info.files_not_being_copied,
                expected_result[folder].files_not_being_copied,
            )
        is_accessible_mock.assert_has_calls(
            [
                *(
                    call(path)
                    for info in expected_result.values()
                    for path in info.files_not_being_copied
                ),
                *(
                    call(path)
                    for info in expected_result.values()
                    for path in info.files_in_progress
                ),
            ],
            any_order=True,
        )
        os_mock.listdir.assert_has_calls(
            [call(dirname) for dirname in target_dirs],
            any_order=True,
        )

    @patch("chia_tea.copy.Disk.is_accessible")
    @patch("chia_tea.copy.Disk.os.path")
    @patch("chia_tea.copy.Disk.os")
    def test_get_files_being_copied_not_being_given_dirs(
        self, os_mock, path_mock, is_accessible_mock
    ):

        target_dirs = {
            "some_file",
        }

        # mock stuff
        os_mock.listdir.return_value = []
        path_mock.join = _path_join
        path_mock.exists.return_value = True
        path_mock.isdir.return_value = False
        path_mock.isfile.return_value = True
        is_accessible_mock.return_value = True

        # do the thing
        result = get_files_being_copied(directories=target_dirs)

        # checks
        self.assertDictEqual(result, {})
        path_mock.exists.assert_called_once_with(next(iter(target_dirs)))
        path_mock.isdir.assert_called_once_with(next(iter(target_dirs)))
        os_mock.listdir.assert_not_called()
        is_accessible_mock.assert_not_called()

    @patch("chia_tea.copy.Disk.is_accessible")
    @patch("chia_tea.copy.Disk.os.path")
    @patch("chia_tea.copy.Disk.os")
    def test_get_files_being_copied_being_given_nonexisting_folders(
        self, os_mock, path_mock, is_accessible_mock
    ):

        target_dirs = {
            "does_not_exist",
        }

        # mock stuff
        os_mock.listdir.return_value = []
        path_mock.join = _path_join
        path_mock.exists.return_value = False
        path_mock.isdir.return_value = True
        path_mock.isfile.return_value = True
        is_accessible_mock.return_value = True

        # do the thing
        result = get_files_being_copied(directories=target_dirs)

        # checks
        self.assertDictEqual(result, {})
        path_mock.exists.assert_called_once_with(next(iter(target_dirs)))
        path_mock.isdir.assert_not_called()
        os_mock.listdir.assert_not_called()
        is_accessible_mock.assert_not_called()
