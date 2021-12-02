import os
import unittest
from unittest.mock import patch

from .Disk import filter_least_used_disks


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
    def test_update_completely_copied_files(self, path_mock):

        target_folders = [
            "folder_a",
            "folder_b",
        ]

        path_mock.join = os.path.join
