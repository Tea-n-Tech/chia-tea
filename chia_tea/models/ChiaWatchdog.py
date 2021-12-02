import copy
import asyncio
from typing import Dict, List

from .FarmerAPI import FarmerAPI
from .HarvesterAPI import HarvesterAPI
from .WalletAPI import WalletAPI
from .FarmerHarvesterLogfile import FarmerHarvesterLogfile
from .MadMaxPlotInProgress import MadMaxPlotInProgress


class ChiaWatchdog:
    """Class for watching chia"""

    # pylint: disable=too-many-instance-attributes

    __logfile_chia_ready: bool = False
    __logfile_madmax_ready: bool = False

    # members related to logfile checking
    harvester_infos: Dict[str, FarmerHarvesterLogfile]
    farmed_blocks: List[str]

    # members related to madmax plotter
    plots_in_progress: List[MadMaxPlotInProgress]

    # members for contacting chia directly
    farmer_service: FarmerAPI
    wallet_service: WalletAPI
    harvester_service: HarvesterAPI

    def __init__(self, logfile_filepath: str, madmax_logfile: str):
        """initialize a chia watchdog

        Parameters
        ----------
        logfile_filepath : str
            path to the logfile to watch
        madmax_logfile : str
            path to the madmax logfile to watch
        """
        self.logfile_filepath = logfile_filepath
        self.madmax_logfile = madmax_logfile
        self.harvester_infos = {}
        self.farmer_service = FarmerAPI()
        self.wallet_service = WalletAPI()
        self.harvester_service = HarvesterAPI()
        self.farmed_blocks = []
        self.plots_in_progress = []

    async def ready(self):
        """Wait for the readiness of the watchdog"""
        while not (
            self.__logfile_chia_ready
            and self.__logfile_madmax_ready
            and self.harvester_service.is_ready
            and self.farmer_service.is_ready
            and self.wallet_service.is_ready
        ):
            await asyncio.sleep(0.25)

    def set_chia_logfile_is_ready(self):
        """When the chia logfile scanner has done its init, this gets called"""
        self.__logfile_chia_ready = True

    def set_madmax_logfile_is_ready(self):
        """When the madmax logfile scanner has done its init, this gets called"""
        self.__logfile_madmax_ready = True

    def get_or_create_harvester_info(
        self,
        harvester_id: str,
        ip_address: str,
    ) -> FarmerHarvesterLogfile:
        """Get or create a harvester info

        Parameters
        ----------
        harvester_id : str
            id of the harvester
        ip_address : str
            ip address

        Returns
        -------
        harvester_info : FarmerHarvesterLogfile
            existing or newly created harvester info
        """

        harvester_info = self.harvester_infos.get(harvester_id)

        #  does not exist yet
        if harvester_info is None:
            harvester_info = FarmerHarvesterLogfile(
                harvester_id=harvester_id,
                ip_address=ip_address,
            )
            self.harvester_infos[harvester_id] = harvester_info
        else:
            # make sure ip is updated
            harvester_info.ip_address = ip_address

        return harvester_info

    def snapshot(self) -> "ChiaWatchdog":
        """Takes a snapshot of the current watchdog

        Returns
        -------
        snapshot : ChiaWatchdog
            copy snapshot
        """
        return copy.deepcopy(self)
