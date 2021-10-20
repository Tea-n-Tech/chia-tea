import unittest

from mock import mock_open, patch

from ...utils.testing import async_test
from .file_watching import watch_logfile_generator


class TestChiaWatchdog(unittest.TestCase):
    @async_test
    async def test_watch_logfile_generator_startup(self):

        lines = [
            "A",
            "B",
        ]

        with patch("builtins.open", mock_open(read_data="\n".join(lines))):
            line_generator = watch_logfile_generator("", on_ready=None)

            i_line = 0
            async for line in line_generator:
                line = line.replace("\n", "")
                self.assertEqual(line, lines[i_line])
                i_line += 1

                if i_line == len(lines):
                    break

            # TODO test on ready and file replacement
