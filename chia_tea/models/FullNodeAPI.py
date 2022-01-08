from dataclasses import dataclass


@dataclass
class FullNodeAPI:
    """FullNodeAPI tracks data derived from the API if a full node
    running on the system.
    """

    # pylint: disable=too-few-public-methods

    is_ready: bool = False
    is_running: bool = False

    # syncing
    is_synced: bool = False
    sync_progress_height: int = 0
    sync_blockchain_height: int = 0
