import unittest
from datetime import datetime

from ..protobuf.generated.chia_pb2 import PlotInProgress
from .formatting import plot_in_progress_pb2_as_markdown


class TestFormatting(unittest.TestCase):
    def test_plot_in_progress_pb2_as_markdown(self):

        plot_in_progress = PlotInProgress(
            id="some-id",
            pool_public_key="some-pool-key",
            start_time=datetime.now().timestamp(),
            state="Phase1",
            progress=0.1,
        )
        output = plot_in_progress_pb2_as_markdown(plot_in_progress=plot_in_progress)

        self.assertIn("Plot some-id", output)
        self.assertIn("Since: ", output)
        self.assertIn("State: Phase1", output)
        self.assertIn("Progress: 10.0%", output)
