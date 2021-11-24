import unittest
from unittest.mock import patch

from typer.testing import CliRunner

from ..utils.config import DEFAULT_CONFIG_FILEPATH
from .main import app

runner = CliRunner()


class TestCopyCmd(unittest.TestCase):
    @patch("chia_tea.cli.copy.run_copy")
    def test_copy_cmd_runs(self, run_copy_mock):
        result = runner.invoke(app, ["copy"])
        run_copy_mock.assert_called_once_with(filepath=DEFAULT_CONFIG_FILEPATH)

        run_copy_mock.reset_mock()
        config_filepath = "some/path/to/config.yml"
        result = runner.invoke(app, ["copy", "--config", config_filepath])
        self.assertEqual(result.exit_code, 0)
        run_copy_mock.assert_called_once_with(filepath=config_filepath)

    @patch("chia_tea.cli.copy.run_copy")
    def test_copy_cmd_interrupted_by_keyboard(self, run_copy_mock):
        run_copy_mock.side_effect = KeyboardInterrupt()
        result = runner.invoke(app, ["copy"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Stopping copy", result.output)

    @patch("chia_tea.cli.copy.run_copy")
    def test_copy_cmd_some_other_error(self, run_copy_mock):
        err_msg = "Blablabla"
        run_copy_mock.side_effect = Exception(err_msg)
        result = runner.invoke(app, ["copy"])
        # self.assertEqual(result.exit_code, 0)
        self.assertIn("Error", result.output)
        self.assertIn(err_msg, result.output)
