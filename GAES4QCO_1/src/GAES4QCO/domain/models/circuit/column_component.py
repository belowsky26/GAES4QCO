import random
from typing import Iterator
from uuid import UUID

from .gate_component import GateComponent
from ..shared.identity import ColumnComponentId


class ColumnComponent(ColumnComponentId):
    def __init__(self, gates: list[GateComponent] = None, _id: UUID = None ):
        super().__init__(_id)
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
