
from copy import deepcopy
from typing import Iterable, List


class HarvesterAPI:
    """ This class holds chia information fetched through RPC
    from chia services on the same machine
    """
    # pylint: disable=too-few-public-methods

    # This helps us to check if an update happened
    is_ready: bool = False

    is_running: bool = False
    plots: List[dict]
    # Plot layout:
    # {
    #     'file_size': 108878195752,
    #     'filename': 'path/to/blabla.plot',
    #     'plot-seed': '0x00000000...',
    #     'plot_public_key': '0x00000000....',
    #     'pool_contract_puzzle_hash': None,
    #     'pool_public_key': '0x00000000....',
    #     'size': 32,
    #     'time_modified': 1621370658.446281
    # }
    failed_to_open_filenames: List[str]
    not_found_filenames: List[str]
    plot_directories: Iterable[str] = tuple()
    n_proofs: int = 0

    def __init__(self):
        self.plots = []
        self.failed_to_open_filenames = []
        self.not_found_filenames = []

    def copy(self) -> 'HarvesterAPI':
        """ Get a copy of the instance

        Returns
        -------
        harvester : HarvesterAPI
            copy of the instance
        """
        new_harvester = HarvesterAPI()
        new_harvester.is_running = self.is_running
        new_harvester.is_ready = self.is_ready
        new_harvester.plots = deepcopy(self.plots)
        new_harvester.failed_to_open_filenames = list(
            self.failed_to_open_filenames)
        new_harvester.not_found_filenames = list(self.not_found_filenames)
        new_harvester.plot_directories = list(self.plot_directories)
        new_harvester.n_proofs = self.n_proofs
        return new_harvester
