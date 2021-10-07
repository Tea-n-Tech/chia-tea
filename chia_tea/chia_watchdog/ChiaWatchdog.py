import asyncio
from typing import Dict, List

from .api.FarmerAPI import FarmerAPI
from .api.HarvesterAPI import HarvesterAPI
from .api.WalletAPI import WalletAPI
from .logfile.FarmerHarvesterLogfile import FarmerHarvesterLogfile
from .madmax.MadMaxPlotInProgress import MadMaxPlotInProgress


class ChiaWatchdog:
    """Class for watching chia"""

    # pylint: disable=too-many-instance-attributes

    __logfile_watching_ready: bool

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
        self.__logfile_watching_ready = False
        self.farmer_service = FarmerAPI()
        self.wallet_service = WalletAPI()
        self.harvester_service = HarvesterAPI()
        self.farmed_blocks = []

    def copy(self) -> "ChiaWatchdog":
        """Creates a copy of this instance

        Returns
        -------
        new_instance : ChiaWatchdog
            copy of the instance
        """
        new_instance = ChiaWatchdog(self.logfile_filepath, self.madmax_logfile)
        new_instance.harvester_infos = {
            id: harvester_info.copy() for id, harvester_info in self.harvester_infos.items()
        }
        new_instance.plots_in_progress = [plot.copy() for plot in self.plots_in_progress]
        # not sure about this one but ok
        # pylint: disable=protected-access
        # pylint: disable=unused-private-member
        new_instance.__logfile_watching_ready = self.__logfile_watching_ready
        new_instance.farmer_service = self.farmer_service.copy()
        new_instance.wallet_service = self.wallet_service.copy()
        new_instance.harvester_service = self.harvester_service.copy()
        new_instance.farmed_blocks = self.farmed_blocks.copy()

        return new_instance

    async def ready(self):
        """Wait for the readiness of the watchdog"""
        while not (
            self.__logfile_watching_ready
            and self.harvester_service.is_ready
            and self.farmer_service.is_ready
            and self.wallet_service.is_ready
        ):
            await asyncio.sleep(0.25)

    def set_as_ready(self):
        """When we scanned the entire logfile once and caught up set this"""
        self.__logfile_watching_ready = True

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
