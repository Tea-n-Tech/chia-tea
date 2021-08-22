from datetime import datetime
from typing import Union


# pylint: disable=too-many-instance-attributes
class FarmerHarvesterLogfile:
    """Class with compact information about harvesters"""

    # General info
    harvester_id: str = ""
    ip_address: str = ""

    # Tracking of connection status
    is_connected = False

    # Signage point tracking
    time_of_end_of_last_sgn_point: Union[datetime, None]
    time_last_incoming_msg: Union[datetime, None]
    time_last_outgoing_msg: Union[datetime, None]

    # Metrics
    n_responses = 0
    n_overdue_responses = 0

    # Additional tracking
    last_update: datetime

    def __init__(
        self,
        harvester_id: str,
        ip_address: str,
        is_connected: bool = False,
        last_update: datetime = datetime.now(),
        time_of_end_of_last_sgn_point: Union[datetime, None] = None,
        time_last_incoming_msg: Union[datetime, None] = None,
        time_last_outgoing_msg: Union[datetime, None] = None,
        timed_out: bool = False,
        n_responses: int = 0,
        n_overdue_responses: int = 0,
    ):
        """Initializes the harvester info

        Parameters
        ----------
        harvester_id : str
            id of the harvester
        ip_address : str
            ip address of the harvester
        last_update: datetime
            timestamp when creation happened
        time_of_incoming_messages : Union[List[datetime], None]
            timestamps when messages came in from the harvester
        time_of_outgoing_messages : Union[List[datetime], None]
            timestamps when messages were sent to the harvester
        timed_out : bool
            if the harvester timed out
        time_of_timeout : Union[datetime, None]
            time of last timeout
        """
        # pylint: disable=too-many-arguments
        self.harvester_id = harvester_id
        self.ip_address = ip_address
        self.is_connected = is_connected
        self.last_update = last_update
        self.time_of_end_of_last_sgn_point = time_of_end_of_last_sgn_point
        self.time_last_incoming_msg = time_last_incoming_msg
        self.time_last_outgoing_msg = time_last_outgoing_msg
        self.timed_out = timed_out
        self.n_responses = n_responses
        self.n_overdue_responses = n_overdue_responses
        self.reset_times()

    def copy(self):
        """ Get a copy of the HarvesterInfo

        Returns
        -------
        harvester_info : HarbesterInfo
            copy of this instance
        """
        return FarmerHarvesterLogfile(
            harvester_id=self.harvester_id,
            ip_address=self.ip_address,
            is_connected=self.is_connected,
            last_update=self.last_update,
            time_of_end_of_last_sgn_point=self.time_of_end_of_last_sgn_point,
            time_last_incoming_msg=self.time_last_incoming_msg,
            time_last_outgoing_msg=self.time_last_outgoing_msg,
            timed_out=self.timed_out,
            n_responses=self.n_responses,
            n_overdue_responses=self.n_overdue_responses
        )

    def check_for_timeout(self, current_time: datetime) -> None:
        """ This functions checks if the harvester timed out from the view of a farmer

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
                delta_seconds = (
                    current_time-self.time_last_incoming_msg).total_seconds()
                if delta_seconds > CHALLENGE_TIMEOUT:
                    self.n_overdue_responses += 1
                if delta_seconds > HARVESTER_TIMOUT:
                    self.timed_out = True

    def reset_times(self):
        """ Resets time of incoming, outgoing msgs and signage points
        """
        self.time_last_outgoing_msg = None
        self.time_last_incoming_msg = None
        self.time_of_end_of_last_sgn_point = None
