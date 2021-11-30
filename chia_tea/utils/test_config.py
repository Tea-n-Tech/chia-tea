import unittest

from .config import get_default_config


class TestConfig(unittest.TestCase):
    def setUp(self) -> None:
        # pylint: disable=invalid-name
        self.maxDiff = None

    def test_default_config_is_valid(self):
        # pylint: disable=no-self-use

        # Should simply not throw an exception since internally
        # it parses a string to a protobuf message.
        get_default_config(certificate_folder="some/folder")
