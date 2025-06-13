import random
from typing import Iterator

from GAES4QCO_1.src.GAES4QCO.domain.models.gate_component import GateComponent


class ColumnComponent:
    def __init__(self, gates: list[GateComponent] = None ):
        self.gates = gates if gates is not None else []

    def add_gate(self, gate: GateComponent):
        self.gates.append(gate)

    def remove_gate(self, gate: GateComponent):
        self.gates.remove(gate)

    def choose_gates(self, count: int = 1) -> GateComponent:
        return random.sample(self.gates, count)

    def get_gates(self) -> Iterator[GateComponent]:
        for gate in self.gates:
            yield gate
