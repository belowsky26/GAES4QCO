from random import random
from uuid import UUID

from qiskit.circuit import QuantumCircuit

from .column_component import ColumnComponent
from ..shared.identity import CircuitId


class Circuit(CircuitId):
    def __init__(self, count_qubits: int = 4, depth: int = 0, columns_components: list[ColumnComponent] = [], apply_evolutionary_strategy: bool = False, fitness: float = 0., _id: UUID = None):
        super().__init__(_id)
        self.count_qubits = count_qubits
        self.columns_components = columns_components
        self.apply_evolutionary_strategy = apply_evolutionary_strategy
        self.fitness = fitness

    def build(self):
        circuit = QuantumCircuit(self.count_qubits)
        for column in self.columns_components:
            for gate_component in column.get_gates():
                gate, qubits = gate_component.build()
                circuit.append(gate, qubits)
        return circuit

    def append_column(self, column: ColumnComponent):
        self.columns_components.append(column)

    def set_fitness(self, fitness: float):
        self.fitness = fitness

    @property
    def depth(self) -> int:
        return len(self.columns_components)