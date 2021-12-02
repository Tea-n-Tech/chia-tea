import unittest
from unittest.mock import patch

from typer.testing import CliRunner

from ..utils.config import DEFAULT_CONFIG_FILEPATH
from .main import app

runner = CliRunner()


class TestConfigCmd(unittest.TestCase):
    @patch("chia_tea.cli.config.create_default_config")
    def test_config_init_creates_default_config_correctly(self, create_default_config_mock):
        overwrite = False

        result = runner.invoke(app, ["config", "init"])
        create_default_config_mock.assert_called_once_with(
            filepath=DEFAULT_CONFIG_FILEPATH,
            overwrite=overwrite,
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("👍", result.output)

    @patch("chia_tea.cli.config.create_default_config")
    def test_config_init_creates_custom_config_correctly(self, create_default_config_mock):
        overwrite = False
        config_filepath = "./blabla/config.yml"

        result = runner.invoke(
            app,
            ["config", "init", "--filepath", config_filepath],
        )
        create_default_config_mock.assert_called_once_with(
            filepath=config_filepath,
            overwrite=overwrite,
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("👍", result.output)

    @patch("chia_tea.cli.config.create_default_config")
    def test_config_init_handles_an_existing_file_correctly(self, create_default_config_mock):

        overwrite = False
        err_msg = "Config file already exists ..."
        create_default_config_mock.side_effect = FileExistsError(err_msg)

        result = runner.invoke(
            app,
            ["config", "init"],
        )
        create_default_config_mock.assert_called_once_with(
            filepath=DEFAULT_CONFIG_FILEPATH,
            overwrite=overwrite,
        )
        self.assertEqual(result.exit_code, 1)
        self.assertIn("⛈️", result.output)
        self.assertIn(err_msg, result.output)

    @patch("chia_tea.cli.config.create_default_config")
    def test_config_init_would_overwrite_if_asked(self, create_default_config_mock):
        overwrite = True
        result = runner.invoke(
            app,
            ["config", "init", "--overwrite"],
        )
        create_default_config_mock.assert_called_once_with(
            filepath=DEFAULT_CONFIG_FILEPATH,
            overwrite=overwrite,
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("👍", result.output)
