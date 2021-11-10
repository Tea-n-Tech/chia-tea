import os
import tempfile
import unittest

from ..utils.testing import async_test
from .file_watching import watch_logfile_generator


class TestChiaWatchdog(unittest.TestCase):
    @async_test
    async def test_watch_logfile_generator_startup(self):

        some_list = []

        async def set_ready():
            some_list.append("something")

        lines = [
            "A",
            "B",
        ]

        with tempfile.TemporaryDirectory() as dir_path:
            filepath = os.path.join(dir_path, "test.log")
            with open(filepath, "w", encoding="utf-8") as fp:
                for line in lines:
                    fp.write(line + "\n")

            line_generator = watch_logfile_generator(filepath, on_ready=set_ready)

            for result_line in lines:
                line = await line_generator.asend(None)
                line = line.replace("\n", "")
                self.assertEqual(line, result_line)

            self.assertTrue(len(some_list) != 0)

    @async_test
    async def test_watch_logfile_generator_work_during_rollovers(self):

        some_list = []

        async def set_ready():
            some_list.append("something")

        lines = ["A", "B", "C"]

        with tempfile.TemporaryDirectory() as dir_path:
            filepath = os.path.join(dir_path, "test.log")
            filepath_rollover = os.path.join(dir_path, "test_1.log")
            with open(filepath, "w", encoding="utf-8") as fp:
                for line in lines[:-1]:
                    fp.write(line + "\n")

            line_generator = watch_logfile_generator(filepath, on_ready=set_ready)

            for result_line in lines[:-1]:
                line = await line_generator.asend(None)
                line = line.replace("\n", "")
                self.assertEqual(line, result_line)

            self.assertTrue(len(some_list) != 0)

            # do rollover
            os.rename(filepath, filepath_rollover)
            with open(filepath, "w", encoding="utf-8") as fp:
                fp.write(lines[-1] + "\n")

            line = await line_generator.asend(None)
            line = line.replace("\n", "")
            self.assertEqual(line, lines[-1])
