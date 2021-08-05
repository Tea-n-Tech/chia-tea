
from typing import List
from .HarvesterConnectedToFarmer import HarvesterConnectedToFarmer


class FarmerService:
    is_ready: bool = False
    is_running: bool = False
    connections: List[HarvesterConnectedToFarmer]

    def __init__(self):
        self.connections = []

    def copy(self) -> 'FarmerService':
        new_farmer = FarmerService()
        new_farmer.is_ready = self.is_ready
        new_farmer.is_running = self.is_running
        new_farmer.connections = [
            connection.copy()
            for connection in self.connections
        ]
        return new_farmer
