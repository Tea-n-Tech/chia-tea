import os
import unittest

import tempfile
from .config import create_default_config, get_default_config
from .testing import set_directory


class TestConfig(unittest.TestCase):
    def setUp(self) -> None:
        # pylint: disable=invalid-name
        self.maxDiff = None

    def test_default_config_is_valid(self):
        # pylint: disable=no-self-use

        # Should simply not throw an exception since internally
        # it parses a string to a protobuf message.
        get_default_config(certificate_folder="some/folder")

    def test_fix_its_ok_if_no_folder_specified(self):
        # pylint: disable=no-self-use

        with tempfile.TemporaryDirectory() as tmp_dir:
            with set_directory(tmp_dir):
                create_default_config(
                    filepath=os.path.join("config.yaml"),
                    overwrite=False,
                )
