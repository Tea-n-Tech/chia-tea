from datetime import datetime, timedelta
from typing import List, Union

from ...utils.logger import get_logger


class FarmerHarvesterLogfile:
    """Class with compact information about harvesters"""

    # General info
    harvester_id: str = ""
    ip_address: str = ""

    # Tracking of connection status
    is_connected = False

    # Signage point tracking
    time_of_incoming_messages: List[datetime]
    time_of_outgoing_messages: List[datetime]

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
        time_of_incoming_messages: Union[List[datetime], None] = None,
        time_of_outgoing_messages: Union[List[datetime], None] = None,
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
        self.harvester_id = harvester_id
        self.ip_address = ip_address
        self.time_of_incoming_messages = (
            [] if time_of_incoming_messages is None
            else time_of_incoming_messages
        )
        self.time_of_outgoing_messages = (
            [] if time_of_outgoing_messages is None
            else time_of_outgoing_messages
        )
        self.is_connected = is_connected
        self.last_update = last_update
        self.timed_out = timed_out
        self.n_responses = n_responses
        self.n_overdue_responses = n_overdue_responses

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
            n_overdue_responses=self.n_overdue_responses,
            n_responses=self.n_responses,
            last_update=self.last_update,
            time_of_incoming_messages=list(self.time_of_incoming_messages),
            time_of_outgoing_messages=list(self.time_of_outgoing_messages),
            timed_out=self.timed_out,
        )

    def get_response_duration(self) -> Union[timedelta, None]:
        """Get the response duration"""

        last_complete_index = self.__index_last_msg_pair

        if last_complete_index is not None:

            delta = self.time_of_incoming_messages[last_complete_index] - \
                self.time_of_outgoing_messages[last_complete_index]

            if delta.total_seconds() < 0:
                get_logger(__file__).warn(
                    "Times of in/out msgs reset b/c of negative timedelta on harvester {}".format(self.harvester_id))
                get_logger(__file__).debug("Last incoming {}".format(
                    self.time_of_incoming_messages[last_complete_index]))
                get_logger(__file__).debug("Last outgoing {}".format(
                    self.time_of_outgoing_messages[last_complete_index]))

            return delta
        else:
            return None

    def check_if_last_response_was_in_time(self) -> None:
        """ Check if latest response time was in time and updates metrics"""
        latestResponseTime = self.get_response_duration()
        if (latestResponseTime is not None):
            latestResponseTimeSeconds = latestResponseTime.total_seconds()
            self.n_responses += 1
            if(latestResponseTimeSeconds > 25):
                self.n_overdue_responses += 1

    @property
    def __index_last_msg_pair(self) -> Union[int, None]:
        """Index of last number msg pairs """
        if (
            self.time_of_incoming_messages
            and self.time_of_outgoing_messages
        ):
            return min(len(self.time_of_incoming_messages),
                       len(self.time_of_outgoing_messages))-1
        return None

    @property
    def time_last_incoming_msg(self) -> Union[datetime, None]:
        """Time when last message came in"""
        if len(self.time_of_incoming_messages):
            return self.time_of_incoming_messages[-1]
        else:
            return None

    @property
    def time_last_outgoing_msg(self) -> Union[datetime, None]:
        """Time when last message to harvester was end"""
        if len(self.time_of_outgoing_messages):
            return self.time_of_outgoing_messages[-1]
        else:
            return None

    def reset(self):
        """Reset the instance by dropping the collected data"""
