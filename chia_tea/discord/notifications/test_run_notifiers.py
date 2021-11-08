import unittest
from unittest import mock

from ...utils.testing import async_test
from .run_notifiers import DISCORD_MSG_LIMIT, MSG_TOO_LONG, log_and_send_msg_if_any


class TestRunNotifiers(unittest.TestCase):
    @async_test
    async def test_log_and_send_msg_if_any(self):
        channel_mock = mock.AsyncMock()
        channel_mock.send.return_value = None
        logger_mock = mock.MagicMock()
        logger_mock.info.return_value = None

        messages = [
            "This is the first message",
            "And this the second",
        ]

        await log_and_send_msg_if_any(
            messages=messages, logger=logger_mock, channel=channel_mock, is_testing=False
        )

        calls = [mock.call(msg) for msg in messages]
        channel_mock.send.assert_has_calls(calls)
        logger_mock.info.assert_has_calls(calls)

    @async_test
    async def test_log_and_send_msg_if_any_msg_too_long(self):
        channel_mock = mock.AsyncMock()
        channel_mock.send.return_value = None
        logger_mock = mock.MagicMock()
        logger_mock.info.return_value = None

        messages = [
            "A" * (DISCORD_MSG_LIMIT + 1),
        ]

        await log_and_send_msg_if_any(
            messages=messages, logger=logger_mock, channel=channel_mock, is_testing=False
        )

        msg = MSG_TOO_LONG.format(n_chars_too_long=1, discord_msg_limit=DISCORD_MSG_LIMIT)
        channel_mock.send.assert_called_once_with(msg)
        logger_mock.info.assert_called_once_with(msg)

    @async_test
    async def test_msg_is_not_sent_to_discord_during_testing(self):
        channel_mock = mock.AsyncMock()
        channel_mock.send.return_value = None
        logger_mock = mock.MagicMock()
        logger_mock.info.return_value = None

        messages = ["Some message"]

        await log_and_send_msg_if_any(
            messages=messages, logger=logger_mock, channel=channel_mock, is_testing=True
        )

        msg = MSG_TOO_LONG.format(n_chars_too_long=1, discord_msg_limit=DISCORD_MSG_LIMIT)
        channel_mock.send.assert_not_called()
        logger_mock.info.assert_called_once_with(messages[0])
