from unittest.mock import patch
from typer.testing import CliRunner
import unittest

from ..utils.config import DEFAULT_CONFIG_FILEPATH
from .main import app

runner = CliRunner()


class TestCopyCmd(unittest.TestCase):
    