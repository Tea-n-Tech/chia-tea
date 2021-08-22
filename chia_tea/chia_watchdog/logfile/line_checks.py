
import traceback
from abc import ABC, abstractmethod
from datetime import datetime

from ...utils.logger import get_logger
from ..ChiaWatchdog import ChiaWatchdog


class AbstractLineAction(ABC):
    """ Action to be applied on log lines """

    @abstractmethod
    def is_match(self, line: str) -> bool:
        """ Checks if a line is matching the Action

        Parameter
        ---------
        line : str
            line to be checked for a match

        Returns
        -------
        is_match : bool
            if the line is a match
        """
        raise NotImplementedError()

    @abstractmethod
    def apply(
            self: str,
            line: str,
            chia_dog: ChiaWatchdog,
    ):
        """ Apply the line action

        Parameter
        ---------
        line : str
            line from which information will be extracted
        harvester_infos : Dict[str, HarvesterInfo]
            harvester infos to be modified by the action
        """
        raise NotImplementedError()


class ActionMessageFromHarvester(AbstractLineAction):
    """ This action is triggered if a farmer sends a msg to a harvester """

    def is_match(self, line: str) -> bool:
        codewords = ("farmer farmer_server",
                     "<-",
                     "farming_info from peer")
        if all(word in line for word in codewords):
            return True
        return False

    def apply(
        self,
        line: str,
        chia_dog: ChiaWatchdog,
    ):

        fragments = line.split()

        # extract data from line
        timestamp = fragments[0]
        timestamp_dt = datetime.fromisoformat(timestamp)
        harvester_id = fragments[-2]
        ip_address = fragments[-1]

        # update info of harvester
        harvester_info = chia_dog.get_or_create_harvester_info(
            harvester_id,
            ip_address
        )

        # First out then in
        harvester_info.time_last_incoming_msg = timestamp_dt
        harvester_info.last_update = timestamp_dt
        harvester_info.is_connected = True
        harvester_info.timed_out = False
        chia_dog.harvester_infos[harvester_id] = harvester_info


class ActionMessageToHarvester(AbstractLineAction):
    """ This action is triggered if a farmer sends a msg to a harvester """

    def is_match(self, line: str) -> bool:
        codewords = ("farmer farmer_server",
                     "->",
                     "new_signage_point_harvester")
        if all(word in line for word in codewords):
            return True
        return False

    def apply(
        self,
        line: str,
        chia_dog: ChiaWatchdog,
    ):
        fragments = line.split()

        # extract data from line
        timestamp = fragments[0]
        timestamp_dt = datetime.fromisoformat(timestamp)
        harvester_id = fragments[-1]
        ip_address = fragments[-2]

        # update info of harvester
        harvester_info = chia_dog.get_or_create_harvester_info(
            harvester_id,
            ip_address
        )

        harvester_info.time_last_outgoing_msg = timestamp_dt
        harvester_info.last_update = timestamp_dt
        chia_dog.harvester_infos[harvester_id] = harvester_info


class ActionFinishedSignagePoint(AbstractLineAction):
    """
    Action is currently used as check if a Harvester is timed out.
    Might be used for SignPoint Metrics at a later stage
    """

    def is_match(self, line: str) -> bool:
        codewords = ("full_node",
                     "Finished signage point")
        if all(word in line for word in codewords):
            return True
        return False

    def apply(
        self,
        line: str,
        chia_dog: ChiaWatchdog,
    ):
        fragments = line.split()

        # extract data from line
        timestamp = fragments[0]
        timestamp_dt = datetime.fromisoformat(timestamp)

        # Harvester Time out Check
        for farmer_harvester_logfile in chia_dog.harvester_infos.values():
            if farmer_harvester_logfile.is_connected:
                farmer_harvester_logfile.check_for_timeout(timestamp_dt)


class ActionHarvesterConnected(AbstractLineAction):
    """ This action is triggered if a farmer connects to a harvester """

    def is_match(self, line: str) -> bool:
        codewords = ("farmer farmer_server", "harvester_handshake to peer")
        if all(word in line for word in codewords):
            return True
        return False

    def apply(
        self,
        line: str,
        chia_dog: ChiaWatchdog,
    ):
        fragments = line.split()

        # extract data from line
        timestamp_dt = datetime.fromisoformat(fragments[0])
        harvester_id = fragments[-1]
        ip_address = fragments[-2]

        # update info of harvester
        harvester_info = chia_dog.get_or_create_harvester_info(
            harvester_id,
            ip_address
        )
        harvester_info.is_connected = True
        harvester_info.timed_out = False
        harvester_info.last_update = timestamp_dt
        chia_dog.harvester_infos[harvester_id] = harvester_info


class ActionHarvesterDisconnected(AbstractLineAction):
    """ This action is triggered if a farmer disconnects to a harvester"""

    def is_match(self, line: str) -> bool:
        codewords = ("farmer farmer_server", "Connection closed")
        if all(word in line for word in codewords):
            return True
        return False

    def apply(
        self,
        line: str,
        chia_dog: ChiaWatchdog,
    ):
        fragments = line.split()

        # extract data from line
        timestamp_dt = datetime.fromisoformat(fragments[0])
        harvester_id = fragments[-1]
        ip_address = fragments[-4]

        # remove suffix
        if ip_address.endswith(","):
            ip_address = ip_address[:-1]

        # update info of harvester
        harvester_info = chia_dog.get_or_create_harvester_info(
            harvester_id,
            ip_address
        )
        harvester_info.is_connected = False
        harvester_info.last_update = timestamp_dt
        chia_dog.harvester_infos[harvester_id] = harvester_info


class ActionHarvesterFoundProof(AbstractLineAction):
    """ This action is triggered if a harvester found a proof """

    # Chia Version: 1.2.0
    # Example:
    #
    # 2021-07-17T13:34:34.513 harvester chia.harvester.harvester: INFO
    # 0 plots were eligible for farming 142fd5714f...
    # Found 0 proofs. Time: 0.00017 s. Total 0 plots

    def is_match(self, line: str) -> bool:
        codewords = ("harvester chia.harvester.harvester",
                     "eligible", "Found", "proofs")
        if all(word in line for word in codewords):
            return True
        return False

    def apply(
        self,
        line: str,
        chia_dog: ChiaWatchdog,
    ):
        fragments = line.split()

        # extract data from line
        proofs = int(fragments[-8])  # interger number

        if proofs > 0:
            harvester_service = chia_dog.harvester_service
            harvester_service.n_proofs += proofs


class ActionFarmedUnfinishedBlock(AbstractLineAction):
    """ This action is triggered if a harvester found a block """

    def is_match(self, line: str) -> bool:
        codewords = ("full_node chia.full_node.full_node",
                     "Farmed unfinished_block")
        if all(word in line for word in codewords):
            return True
        return False

    def apply(
        self,
        line: str,
        chia_dog: ChiaWatchdog,
    ):
        fragments = line.split()

        # extract block id from fragements
        block_id = fragments[-1]
        if block_id not in chia_dog.farmed_blocks:
            chia_dog.farmed_blocks.append(block_id)


async def run_line_checks(chia_dog: ChiaWatchdog, line: str):
    """ Processes a line from the logfile

    Parameters
    ----------
    line : str
        logfile line
    """
    try:
        if chia_dog.is_reset_time():
            chia_dog.reset_data()

        if line:
            for action in ALL_LINE_ACTIONS:
                if action.is_match(line):
                    action.apply(line, chia_dog)

    except Exception:
        trace = traceback.format_exc()
        err_msg = "Error in line: %s\n%s"
        get_logger(__name__).error(err_msg, line, trace)

ALL_LINE_ACTIONS = (
    ActionMessageFromHarvester(),
    ActionMessageToHarvester(),
    ActionFinishedSignagePoint(),
    ActionHarvesterConnected(),
    ActionHarvesterDisconnected(),
    ActionHarvesterFoundProof(),
)
