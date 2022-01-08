from dataclasses import dataclass, field


@dataclass
class FullNodeAPI:
    """ """

    # pylint: disable=too-few-public-methods

    is_ready: bool = False
    is_running: bool = False

    # syncing
    is_synced: bool = False
    sync_progress_height: int = 0
    sync_blockchain_height: int = 0
    sync_progress: float = 0.0
