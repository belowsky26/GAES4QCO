from random import randint

from .gate_builder import GateBuilder
from ..models.circuit.column_component import ColumnComponent


class ColumnBuilder:
    def __init__(self, gate_component_builder: GateBuilder):
        self.gate_builder = gate_component_builder

    def build(self, total_circuit_qubits: int) -> ColumnComponent:
        """Cria uma instância de ColumnComponent."""
        column_gates = []
        available_qubits_in_column = list(range(total_circuit_qubits))

        # Lógica para decidir quantos gates haverá nesta coluna (ex: aleatório)
        num_gates = randint(1, total_circuit_qubits)

        for _ in range(num_gates):
            if not available_qubits_in_column:
                break

            # USA O BUILDER DE NÍVEL MAIS BAIXO para criar um gate
            new_gate_comp = self.gate_builder.build(available_qubits_in_column)
            column_gates.append(new_gate_comp)

            # Atualiza a lista de qubits disponíveis para evitar sobreposição na mesma coluna
            for q in new_gate_comp.qubits:  # Acessa os qubits do componente criado
                if q in available_qubits_in_column:
                    available_qubits_in_column.remove(q)

        return ColumnComponent(gates=column_gates)

    def gen_random_column(self):
        qubits = list(range(self.lim_qubits))
        gates = []
        while qubits:
            gate, qubits = self.gate_builder.build_gate_component(qubits, self.evolutionary_strategies)
            gates.append(gate)
        column_component = ColumnComponent(gates)
        return column_component