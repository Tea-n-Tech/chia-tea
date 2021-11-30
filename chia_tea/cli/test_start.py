import unittest
from unittest.mock import patch

from typer.testing import CliRunner

from ..utils.config import DEFAULT_CONFIG_FILEPATH
from .main import app

runner = CliRunner()


class TestStartCmd(unittest.TestCase):
    # CONFIG

    @patch("chia_tea.cli.start.read_config")
    @patch("chia_tea.cli.start.run_copy")
    def test_copy_cmd_runs(self, run_copy_mock, read_config_mock):
        result = runner.invoke(app, ["start", "copy"])
        read_config_mock.assert_called_once_with(filepath=DEFAULT_CONFIG_FILEPATH)
        run_copy_mock.assert_called_once()

        run_copy_mock.reset_mock()
        read_config_mock.reset_mock()

        config_filepath = "some/path/to/config.yml"
        result = runner.invoke(app, ["start", "copy", "--config", config_filepath])
        self.assertEqual(result.exit_code, 0)
        read_config_mock.assert_called_once_with(filepath=config_filepath)
        run_copy_mock.assert_called_once()

    @patch("chia_tea.cli.start.read_config")
    @patch("chia_tea.cli.start.run_copy")
    def test_copy_cmd_interrupted_by_keyboard(self, run_copy_mock, read_config_mock):
        run_copy_mock.side_effect = KeyboardInterrupt()
        result = runner.invoke(app, ["start", "copy"])
        read_config_mock.assert_called_once_with(filepath=DEFAULT_CONFIG_FILEPATH)
        run_copy_mock.assert_called_once()
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Stopping copy", result.output)

    @patch("chia_tea.cli.start.read_config")
    @patch("chia_tea.cli.start.run_copy")
    def test_copy_cmd_some_other_error(self, run_copy_mock, read_config_mock):
        err_msg = "Blablabla"
        run_copy_mock.side_effect = Exception(err_msg)
        result = runner.invoke(app, ["start", "copy"])
        read_config_mock.assert_called_once_with(filepath=DEFAULT_CONFIG_FILEPATH)
        run_copy_mock.assert_called_once()
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error", result.output)
        self.assertIn(err_msg, result.output)

    # MONITORING CLIENT

    @patch("chia_tea.cli.start.read_config")
    @patch("chia_tea.cli.start.run_monitoring_client")
    def test_monitoring_client_cmd_runs(self, run_monitoring_client_mock, read_config_mock):
        result = runner.invoke(app, ["start", "monitoring-client"])
        read_config_mock.assert_called_once_with(filepath=DEFAULT_CONFIG_FILEPATH)
        run_monitoring_client_mock.assert_called_once()

        run_monitoring_client_mock.reset_mock()
        read_config_mock.reset_mock()

        config_filepath = "some/path/to/config.yml"
        result = runner.invoke(app, ["start", "monitoring-client", "--config", config_filepath])
        self.assertEqual(result.exit_code, 0)
        read_config_mock.assert_called_once_with(filepath=config_filepath)
        run_monitoring_client_mock.assert_called_once()

    @patch("chia_tea.cli.start.read_config")
    @patch("chia_tea.cli.start.run_monitoring_client")
    def test_monitoring_client_cmd_interrupted_by_keyboard(
        self, run_monitoring_client_mock, read_config_mock
    ):
        run_monitoring_client_mock.side_effect = KeyboardInterrupt()
        result = runner.invoke(app, ["start", "monitoring-client"])
        read_config_mock.assert_called_once_with(filepath=DEFAULT_CONFIG_FILEPATH)
        run_monitoring_client_mock.assert_called_once()
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Shutting down", result.output)

    @patch("chia_tea.cli.start.read_config")
    @patch("chia_tea.cli.start.run_monitoring_client")
    def test_monitoring_client_cmd_some_other_error(
        self, run_monitoring_client_mock, read_config_mock
    ):
        err_msg = "Blablabla"
        run_monitoring_client_mock.side_effect = Exception(err_msg)
        result = runner.invoke(app, ["start", "monitoring-client"])
        read_config_mock.assert_called_once_with(filepath=DEFAULT_CONFIG_FILEPATH)
        run_monitoring_client_mock.assert_called_once()
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error", result.output)
        self.assertIn(err_msg, result.output)

    # MONITORING SERVER

    @patch("chia_tea.cli.start.read_config")
    @patch("chia_tea.cli.start.run_monitoring_server")
    def test_monitoring_server_cmd_runs(self, run_monitoring_server_mock, read_config_mock):
        result = runner.invoke(app, ["start", "monitoring-server"])
        read_config_mock.assert_called_once_with(filepath=DEFAULT_CONFIG_FILEPATH)
        run_monitoring_server_mock.assert_called_once()

        run_monitoring_server_mock.reset_mock()
        read_config_mock.reset_mock()

        config_filepath = "some/path/to/config.yml"
        result = runner.invoke(app, ["start", "monitoring-server", "--config", config_filepath])
        self.assertEqual(result.exit_code, 0)
        read_config_mock.assert_called_once_with(filepath=config_filepath)
        run_monitoring_server_mock.assert_called_once()

    @patch("chia_tea.cli.start.read_config")
    @patch("chia_tea.cli.start.run_monitoring_server")
    def test_monitoring_server_cmd_interrupted_by_keyboard(
        self, run_monitoring_server_mock, read_config_mock
    ):
        run_monitoring_server_mock.side_effect = KeyboardInterrupt()
        result = runner.invoke(app, ["start", "monitoring-server"])
        read_config_mock.assert_called_once_with(filepath=DEFAULT_CONFIG_FILEPATH)
        run_monitoring_server_mock.assert_called_once()
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Shutting down", result.output)

    @patch("chia_tea.cli.start.read_config")
    @patch("chia_tea.cli.start.run_monitoring_server")
    def test_monitoring_server_cmd_some_other_error(
        self, run_monitoring_server_mock, read_config_mock
    ):
        err_msg = "Blablabla"
        run_monitoring_server_mock.side_effect = Exception(err_msg)
        result = runner.invoke(app, ["start", "monitoring-server"])
        read_config_mock.assert_called_once_with(filepath=DEFAULT_CONFIG_FILEPATH)
        run_monitoring_server_mock.assert_called_once()
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error", result.output)
        self.assertIn(err_msg, result.output)

    # DISCORD BOT

    @patch("chia_tea.cli.start.read_config")
    @patch("chia_tea.cli.start.run_discord_bot")
    def test_discord_bot_cmd_runs(self, discord_bot_mock, read_config_mock):
        result = runner.invoke(app, ["start", "discord-bot"])
        read_config_mock.assert_called_once_with(filepath=DEFAULT_CONFIG_FILEPATH)
        discord_bot_mock.assert_called_once()

        discord_bot_mock.reset_mock()
        read_config_mock.reset_mock()

        config_filepath = "some/path/to/config.yml"
        result = runner.invoke(app, ["start", "discord-bot", "--config", config_filepath])
        self.assertEqual(result.exit_code, 0)
        read_config_mock.assert_called_once_with(filepath=config_filepath)
        discord_bot_mock.assert_called_once()

    @patch("chia_tea.cli.start.read_config")
    @patch("chia_tea.cli.start.run_discord_bot")
    def test_discord_bot_cmd_interrupted_by_keyboard(self, discord_bot_mock, read_config_mock):
        discord_bot_mock.side_effect = KeyboardInterrupt()
        result = runner.invoke(app, ["start", "discord-bot"])
        read_config_mock.assert_called_once_with(filepath=DEFAULT_CONFIG_FILEPATH)
        discord_bot_mock.assert_called_once()
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Shutting down", result.output)

    @patch("chia_tea.cli.start.read_config")
    @patch("chia_tea.cli.start.run_discord_bot")
    def test_discord_bot_cmd_some_other_error(self, discord_bot_mock, read_config_mock):
        err_msg = "Blablabla"
        discord_bot_mock.side_effect = Exception(err_msg)
        result = runner.invoke(app, ["start", "discord-bot"])
        read_config_mock.assert_called_once_with(filepath=DEFAULT_CONFIG_FILEPATH)
        discord_bot_mock.assert_called_once()
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error", result.output)
        self.assertIn(err_msg, result.output)
