

class FarmerHarvesterAPI:
    """ A connected machine to the farmer

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

    bytes_read: int
    bytes_written: int
    creation_time: float
    last_message_time: float
    local_port: int
    node_id: bytes
    peer_host: str
    peer_port: int
    peer_server_port: int
    type: int
    n_plots: int

    def __init__(
        self,
        bytes_read: int,
        bytes_written: int,
        creation_time: float,
        last_message_time: float,
        local_port: int,
        node_id: bytes,
        peer_host: str,
        peer_port: int,
        peer_server_port: int,
        type: int,
        n_plots: int = 0,
    ):
        # pylint: disable=redefined-builtin, too-many-arguments
        self.bytes_read = bytes_read
        self.bytes_written = bytes_written
        self.creation_time = creation_time
        self.last_message_time = last_message_time
        self.local_port = local_port
        self.node_id = node_id
        self.peer_host = peer_host
        self.peer_port = peer_port
        self.peer_server_port = peer_server_port
        self.type = type
        self.n_plots = n_plots

    def copy(self) -> 'FarmerHarvesterAPI':
        """ Get a copy of the instance

        Returns
        -------
        farmer_harvester : FarmerHarvesterAPI
            copy of the instance
        """
        return FarmerHarvesterAPI(
            **self.__dict__,
        )
