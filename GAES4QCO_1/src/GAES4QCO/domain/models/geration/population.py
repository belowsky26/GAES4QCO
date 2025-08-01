from typing import List
from ..shared.identity import CircuitId

class Population:
    def __init__(self, circuit_ids: List[CircuitId]):
        self.circuit_ids = circuit_ids
        self.size = len(circuit_ids)