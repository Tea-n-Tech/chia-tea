import json
import os
import unittest

from google.protobuf.json_format import MessageToDict

from .config import get_default_config, read_config


class TestConfig(unittest.TestCase):

    def setUp(self) -> None:
        # pylint: disable=invalid-name
        self.maxDiff = None

    def test_default_config_matches_internal_default_config(self):
        internal_default_config = get_default_config()
        other_default_config = read_config(os.path.join(
            os.path.dirname(__file__), "..", "..", "config_default.yml"))

        self.assertEqual(
            json.dumps(MessageToDict(internal_default_config), indent=2),
            json.dumps(MessageToDict(other_default_config), indent=2)
        )
