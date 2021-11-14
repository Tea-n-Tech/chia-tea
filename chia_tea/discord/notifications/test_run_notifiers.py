import asyncio
import unittest
from unittest import mock

from ...utils.testing import async_test
from .run_notifiers import DISCORD_MSG_LIMIT, MSG_TOO_LONG, log_and_send_msg_if_any


def _get_future(obj):
    f = asyncio.Future()
    f.set_result(obj)
    return f


class TestRunNotifiers(unittest.TestCase):

    # pylint: disable=no-self-use
    @async_test
    async def test_msg_is_sent(self):
        channel_mock = mock.MagicMock()
        channel_mock.send.return_value = _get_future(None)
        logger_mock = mock.MagicMock()
        logger_mock.info.return_value = None

        messages = [
            "This is the first message",
        ]

        await log_and_send_msg_if_any(
            messages=messages, logger=logger_mock, channel=channel_mock, is_testing=False
        )

        calls = [mock.call(msg) for msg in messages]
        channel_mock.send.assert_has_calls(calls)
        logger_mock.info.assert_has_calls(calls)

    # pylint: disable=no-self-use
    @async_test
    async def test_log_and_send_msg_if_any_msg_too_long(self):
        channel_mock = mock.MagicMock()
        channel_mock.send.return_value = _get_future(None)
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

    # pylint: disable=no-self-use
    @async_test
    async def test_msg_is_not_sent_to_discord_during_testing(self):
        channel_mock = mock.MagicMock()
        channel_mock.send.return_value = _get_future(None)
        logger_mock = mock.MagicMock()
        logger_mock.info.return_value = None

        messages = ["Some message"]

        await log_and_send_msg_if_any(
            messages=messages, logger=logger_mock, channel=channel_mock, is_testing=True
        )

        channel_mock.send.assert_not_called()
        logger_mock.info.assert_called_once_with(messages[0])

    # pylint: disable=no-self-use
    @async_test
    async def test_multiple_messages_are_bundled(self):
        channel_mock = mock.MagicMock()
        channel_mock.send.return_value = _get_future(None)
        logger_mock = mock.MagicMock()
        logger_mock.info.return_value = None

        messages = ["This is the first message", "This is the second message"]
        total_msg = "\n".join(messages)

        await log_and_send_msg_if_any(
            messages=messages, logger=logger_mock, channel=channel_mock, is_testing=False
        )

        channel_mock.send.assert_called_once_with(total_msg)
        logger_mock.info.assert_called_once_with(total_msg)

    # pylint: disable=no-self-use
    @async_test
    async def test_multiple_messages_are_sent_individually_if_too_long(self):
        channel_mock = mock.MagicMock()
        channel_mock.send.return_value = _get_future(None)
        logger_mock = mock.MagicMock()
        logger_mock.info.return_value = None

        messages = ["A" * 1000, "A" * 1001]

        await log_and_send_msg_if_any(
            messages=messages, logger=logger_mock, channel=channel_mock, is_testing=False
        )

        calls = [mock.call(msg) for msg in messages]
        channel_mock.send.assert_has_calls(calls)
        logger_mock.info.assert_has_calls(calls)
