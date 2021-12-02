from dataclasses import dataclass, field
from typing import Iterable, List


@dataclass
class HarvesterAPI:
    """This class holds chia information fetched through RPC
    from chia services on the same machine
    """

    # pylint: disable=too-few-public-methods

    # This helps us to check if an update happened
    is_ready: bool = False

    is_running: bool = False
    plots: List[dict] = field(default_factory=list)
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
    failed_to_open_filenames: List[str] = field(default_factory=list)
    not_found_filenames: List[str] = field(default_factory=list)
    plot_directories: Iterable[str] = tuple()
    n_proofs: int = 0
