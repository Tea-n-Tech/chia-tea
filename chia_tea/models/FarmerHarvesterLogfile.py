from dataclasses import dataclass
from datetime import datetime
from typing import Optional


# pylint: disable=too-many-instance-attributes
@dataclass
class FarmerHarvesterLogfile:
    """Class with compact information about harvesters"""

    # General info
    harvester_id: str = ""
    ip_address: str = ""

    # Tracking of connection status
    is_connected: bool = False

    # Signage point tracking
    time_of_end_of_last_sgn_point: Optional[datetime] = None
    time_last_incoming_msg: Optional[datetime] = None
    time_last_outgoing_msg: Optional[datetime] = None
    timed_out: bool = False

    # Metrics
    n_responses: int = 0
    n_overdue_responses: int = 0

    # Additional tracking
    last_update: datetime = datetime.now()

    def check_for_timeout(self, current_time: datetime) -> None:
        """This functions checks if the harvester timed out from the view of a farmer

        Parameters
        ----------
        current_time : datetime
            current time to base computation on

        Notes
        -----
            Modifies internal attributes so don't spam.
        """
        CHALLENGE_TIMEOUT = 25  # seconds
        HARVESTER_TIMOUT = 60  # seconds

        if not self.timed_out:
            if self.time_last_incoming_msg is not None and self.time_last_outgoing_msg is not None:
                delta_seconds = (current_time - self.time_last_incoming_msg).total_seconds()
                if delta_seconds > CHALLENGE_TIMEOUT:
                    self.n_overdue_responses += 1
                if delta_seconds > HARVESTER_TIMOUT:
                    self.timed_out = True
