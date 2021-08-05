
from chia_tea.utils.logger import get_logger
from datetime import datetime

from .HarvesterInfo import HarvesterInfo


def check_timeout(harvester_info: HarvesterInfo):
    """ Check if the harvester timed out

    Parameters
    ----------
    harvester_info : HarvesterInfo
        harvester to be checked
    """

    timeout = 60

    time_last_incoming_msg = harvester_info.time_last_incoming_msg

    # optional - seconds since last timeout - works as rate limiter
    seconds_since_last_timeout = 0
    if harvester_info.time_of_timeout is not None:
        seconds_since_last_timeout = datetime.now() - harvester_info.time_of_timeout

    if time_last_incoming_msg:
        seconds_since_update = (
            datetime.now() - time_last_incoming_msg).total_seconds()

        if harvester_info.is_connected and not harvester_info.timed_out \
                and seconds_since_update > timeout and seconds_since_last_timeout > timeout:
            get_logger(__file__).debug("Harvester {} timed out due to late send. Seconds since last send: {}".format(
                harvester_info.harvester_id, seconds_since_update))
            harvester_info.timed_out = True
            harvester_info.n_timeouts += 1
            harvester_info.time_of_timeout = datetime.now()
        elif harvester_info.is_connected and seconds_since_update < timeout:
            harvester_info.timed_out = False


ALL_HARVESTER_CHECKS = [
    check_timeout
]
