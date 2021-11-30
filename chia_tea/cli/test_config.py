import os
import unittest
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from ..utils.config import DEFAULT_CONFIG_FILEPATH
from .main import app

runner = CliRunner()


def assert_certificate_generated(
    dirpath: str, overwrite: bool, create_certificate_pair_mock: MagicMock
):
    """Asserts that the certificate generation fn was called correctly"""
    key_path = os.path.join(dirpath, "server.key")
    cert_path = os.path.join(dirpath, "server.crt")
    create_certificate_pair_mock.assert_called_once_with(
        key_path=key_path, cert_path=cert_path, overwrite=overwrite
    )


class TestConfigCmd(unittest.TestCase):
    @patch("chia_tea.cli.config.create_certificate_pair")
    @patch("chia_tea.cli.config.create_default_config")
    def test_config_init_creates_default_config_correctly(
        self, create_default_config_mock, create_certificate_pair_mock
    ):
        overwrite = False

        result = runner.invoke(app, ["config", "init"])
        create_default_config_mock.assert_called_once_with(
            filepath=DEFAULT_CONFIG_FILEPATH,
            overwrite=overwrite,
        )
        assert_certificate_generated(
            dirpath=os.path.dirname(DEFAULT_CONFIG_FILEPATH),
            overwrite=overwrite,
            create_certificate_pair_mock=create_certificate_pair_mock,
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("👍", result.output)

    @patch("chia_tea.cli.config.create_certificate_pair")
    @patch("chia_tea.cli.config.create_default_config")
    def test_config_init_creates_custom_config_correctly(
        self, create_default_config_mock, create_certificate_pair_mock
    ):
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
        assert_certificate_generated(
            dirpath=os.path.dirname(config_filepath),
            overwrite=overwrite,
            create_certificate_pair_mock=create_certificate_pair_mock,
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("👍", result.output)

    @patch("chia_tea.cli.config.create_certificate_pair")
    @patch("chia_tea.cli.config.create_default_config")
    def test_config_init_handles_an_existing_file_correctly(
        self, create_default_config_mock, create_certificate_pair_mock
    ):

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
        create_certificate_pair_mock.assert_not_called()
        self.assertEqual(result.exit_code, 1)
        self.assertIn("⛈️", result.output)
        self.assertIn(err_msg, result.output)

    @patch("chia_tea.cli.config.create_certificate_pair")
    @patch("chia_tea.cli.config.create_default_config")
    def test_config_init_would_overwrite_if_asked(
        self, create_default_config_mock, create_certificate_pair_mock
    ):
        overwrite = True
        result = runner.invoke(
            app,
            ["config", "init", "--overwrite"],
        )
        create_default_config_mock.assert_called_once_with(
            filepath=DEFAULT_CONFIG_FILEPATH,
            overwrite=overwrite,
        )
        assert_certificate_generated(
            os.path.dirname(DEFAULT_CONFIG_FILEPATH),
            overwrite=overwrite,
            create_certificate_pair_mock=create_certificate_pair_mock,
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("👍", result.output)
