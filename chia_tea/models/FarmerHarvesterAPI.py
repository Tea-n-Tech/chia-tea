from dataclasses import dataclass


@dataclass
class FarmerHarvesterAPI:
    """A connected machine to the farmer

    schema of connections from example data
    {
        'bytes_read': 732920,
        'bytes_written': 736979,
        'creation_time': 1625781881.464225,
        'last_message_time': 1625856666.3932514,
        'local_port': 8447,
        'node_id': b'1n\x0f\xc4J\xb5q8\xc4\x98\x0b\xe7\\\xac\xd1\x82...',
        'peer_host': '127.0.0.1',
        'peer_port': 51844,
        'peer_server_port': 8448,
        'type': 2
    }
    """

    # pylint: disable=too-few-public-methods, too-many-instance-attributes

    node_id: bytes
    bytes_read: int
    bytes_written: int
    creation_time: float
    last_message_time: float
    local_port: int
    peer_host: str
    peer_port: int
    peer_server_port: int
    type: int

    # self-added extra attributes
    n_plots: int = 0
