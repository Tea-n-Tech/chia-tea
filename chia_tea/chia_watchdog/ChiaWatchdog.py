import asyncio
from datetime import date
from typing import Dict, List, Union

from ..utils.logger import get_logger
from .api.FarmerAPI import FarmerAPI
from .api.HarvesterAPI import HarvesterAPI
from .api.WalletAPI import WalletAPI
from .logfile.FarmerHarvesterLogfile import FarmerHarvesterLogfile


class ChiaWatchdog:
    """Class for watching chia"""

    date_last_reset: date
    __logfile_watching_ready: bool

    # members related to logfile checking
    harvester_infos: Dict[str, FarmerHarvesterLogfile]

    # members for contacting chia directly
    farmer_service: FarmerAPI
    wallet_service: WalletAPI
    harvester_service: HarvesterAPI

    # TODO check if we still need this
    farmed_blocks: List[str]

    def __init__(self, logfile_filepath: str):
        """ initialize a chia watchdog

        Parameters
        ----------
        logfile_filepath : str
            path to the logfile to watch
        """
        self.logfile_filepath = logfile_filepath
        self.harvester_infos = {}
        self.date_last_reset = date.today()
        self.__logfile_watching_ready = False
        self.farmer_service = FarmerAPI()
        self.wallet_service = WalletAPI()
        self.harvester_service = HarvesterAPI()
        self.farmed_blocks = []

    def copy(self) -> 'ChiaWatchdog':
        """ Creates a copy of this instance

        Returns
        -------
        new_instance : ChiaWatchdog
            copy of the instance
        """
        new_instance = ChiaWatchdog(self.logfile_filepath)
        new_instance.harvester_infos = {
            id: harvester_info.copy()
            for id, harvester_info in self.harvester_infos.items()
        }
        # date is immutable thus safe to share
        new_instance.date_last_reset = self.date_last_reset
        # not sure about this one but ok
        new_instance.__logfile_watching_ready = self.__logfile_watching_ready
        new_instance.farmer_service = self.farmer_service.copy()
        new_instance.wallet_service = self.wallet_service.copy()
        new_instance.harvester_service = self.harvester_service.copy()
        new_instance.farmed_blocks = self.farmed_blocks.copy()

        return new_instance

    async def ready(self):
        """ Wait for the readiness of the watchdog
        """
        # TODO refactor this
        while not (self.__logfile_watching_ready and
                   self.harvester_service.is_ready and
                   self.farmer_service.is_ready and
                   self.wallet_service.is_ready):
            await asyncio.sleep(0.25)

    def set_as_ready(self):
        self.__logfile_watching_ready = True

    def is_reset_time(self) -> bool:
        """If it is already midnight we need to reset to prevent data overflow"""
        # TODO change to FIFO queue
        date_right_now = date.today()
        if (date_right_now - self.date_last_reset).total_seconds():
            return True
        else:
            return False

    def reset_data(self):
        """ Reset the watchdogs data """
        get_logger(__name__).debug("Resetting harvester data.")
        self.harvester_infos = {}
        self.date_last_reset = date.today()
        self.farmed_blocks = []

    def get_or_create_harvester_info(
        self,
        id: str,
        ip_address: str,
    ) -> FarmerHarvesterLogfile:
        """ Get or create a harvester info

        Parameters
        ----------
        id : str
            id of the harvester
        ip_address : str
            ip address

        Returns
        -------
        harvester_info : FarmerHarvesterLogfile
            existing or newly created harvester info
        """

        harvester_info = self.harvester_infos.get(id)

        #  does not exist yet
        if harvester_info is None:
            harvester_info = FarmerHarvesterLogfile(
                harvester_id=id,
                ip_address=ip_address,
            )
            self.harvester_infos[id] = harvester_info
        else:
            # make sure ip is updated
            harvester_info.ip_address = ip_address

        return harvester_info
