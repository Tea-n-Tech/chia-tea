from dataclasses import dataclass, field
from typing import List

from .FarmerHarvesterAPI import FarmerHarvesterAPI


@dataclass
class FarmerAPI:
    """This class holds chia information fetched through RPC
    from chia services on the same machine
    """

    # pylint: disable=too-few-public-methods

    is_ready: bool = False
    is_running: bool = False
    connections: List[FarmerHarvesterAPI] = field(default_factory=list)
