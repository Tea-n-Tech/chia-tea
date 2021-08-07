
from typing import List
from .FarmerHarvesterAPI import FarmerHarvesterAPI


class FarmerAPI:
    is_ready: bool = False
    is_running: bool = False
    connections: List[FarmerHarvesterAPI]

    def __init__(self):
        self.connections = []

    def copy(self) -> 'FarmerAPI':
        new_farmer = FarmerAPI()
        new_farmer.is_ready = self.is_ready
        new_farmer.is_running = self.is_running
        new_farmer.connections = [
            connection.copy()
            for connection in self.connections
        ]
        return new_farmer
